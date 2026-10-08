# /// script
# requires-python = ">=3.11"
# dependencies = ["tree-sitter>=0.25,<0.27", "tree-sitter-java>=0.23.5,<0.24"]
# ///

"""Print a bounded, parser-derived view of Java type relationships.

Types are traversed through inheritance, fields, and signatures. Project types
referenced only in method bodies are listed in body_references and are not
traversed."""

import argparse
import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path

import tree_sitter_java
from tree_sitter import Language, Parser


TYPE_KINDS = {
    "class_declaration": "class",
    "interface_declaration": "interface",
    "enum_declaration": "enum",
    "record_declaration": "record",
    "annotation_type_declaration": "annotation",
}
IGNORED_DIRS = {".git", ".gradle", ".idea", "build", "node_modules", "out", "target"}
RELATION_ORDER = {"extends": 0, "implements": 1, "field": 2, "signature": 3}
UNRESOLVED_SAMPLE_LIMIT = 30
RECEIVER_OWNERS = {"method_invocation", "field_access"}


def source_text(source, node):
    return source[node.start_byte : node.end_byte].decode("utf-8")


def type_names(source, node):
    if node is None:
        return []
    if node.type == "type_identifier":
        return [source_text(source, node)]
    if node.type == "scoped_type_identifier":
        parts = []
        arguments = []
        for child in node.named_children:
            names = type_names(source, child)
            if names:
                parts.append(names[0])
                arguments.extend(names[1:])
        return [".".join(parts), *arguments]
    names = []
    for child in node.named_children:
        names.extend(type_names(source, child))
    return names


def java_files(project_root):
    paths = []
    for directory, names, filenames in os.walk(project_root):
        names[:] = sorted(name for name in names if name not in IGNORED_DIRS and not name.startswith("."))
        for filename in sorted(filenames):
            if filename.endswith(".java"):
                paths.append(Path(directory) / filename)
    return paths


def file_index(paths):
    index = defaultdict(list)
    for path in paths:
        index[path.stem].append(path)
    return index


def candidate_paths(qualified_name, index):
    parts = qualified_name.split(".")
    for outer_position in range(len(parts) - 1, -1, -1):
        outer_name = parts[outer_position]
        suffix = (*parts[:outer_position], outer_name + ".java")
        matches = [
            path for path in index.get(outer_name, [])
            if path.parts[-len(suffix) :] == suffix
        ]
        if matches:
            return matches
    return []


def declarations(container):
    for child in container.named_children:
        if child.type in TYPE_KINDS:
            yield child
        elif child.type == "enum_body_declarations":
            yield from declarations(child)


def load_file(path, parser, cache):
    if path in cache:
        return cache[path]
    source = path.read_bytes()
    tree = parser.parse(source)
    if tree.root_node.has_error:
        raise ValueError(f"Java syntax error in {path}")
    package = ""
    imports = {}
    wildcard_imports = []
    for node in tree.root_node.named_children:
        if node.type == "package_declaration":
            package = source_text(source, node.named_children[-1])
        elif node.type == "import_declaration":
            declaration = source_text(source, node)
            if declaration.startswith("import static "):
                continue
            imported = source_text(source, node.named_children[0])
            if declaration.rstrip().endswith(".*;"):
                wildcard_imports.append(imported)
            else:
                imports[imported.rsplit(".", 1)[-1]] = imported
    result = (source, tree.root_node, package, imports, sorted(set(wildcard_imports)))
    cache[path] = result
    return result


def find_declaration(root, source, package, qualified_name):
    prefix = package + "." if package else ""
    if not qualified_name.startswith(prefix):
        return None
    type_path = qualified_name[len(prefix) :].split(".")
    container = root
    declaration = None
    for position, segment in enumerate(type_path):
        declaration = next(
            (
                node for node in declarations(container)
                if source_text(source, node.child_by_field_name("name")) == segment
            ),
            None,
        )
        if declaration is None:
            return None
        container = declaration.child_by_field_name("body")
        if container is None and position < len(type_path) - 1:
            return None
    return declaration


def type_parameters(declaration, source):
    parameters = declaration.child_by_field_name("type_parameters")
    if parameters is None:
        return set()
    return {
        source_text(source, child.named_children[0])
        for child in parameters.named_children
        if child.type == "type_parameter" and child.named_children
    }


def parameter_types(parameters, source):
    names = []
    if parameters is None:
        return names
    for parameter in parameters.named_children:
        type_node = parameter.child_by_field_name("type")
        if type_node is not None:
            names.extend(type_names(source, type_node))
        elif parameter.type == "spread_parameter":
            names.extend(type_names(source, parameter))
    return names


def hierarchy_references(container, source, relation):
    refs = set()
    if container is None:
        return refs
    type_list = next(
        (child for child in container.named_children if child.type == "type_list"), None
    )
    types = type_list.named_children if type_list is not None else container.named_children
    for type_node in types:
        names = type_names(source, type_node)
        if names:
            refs.add((relation, names[0]))
            refs.update(("signature", name) for name in names[1:])
    return refs


def references(declaration, source):
    refs = set()
    kind = TYPE_KINDS[declaration.type]
    superclass = declaration.child_by_field_name("superclass")
    refs.update(hierarchy_references(superclass, source, "extends"))
    for child in declaration.named_children:
        if child.type == "extends_interfaces":
            refs.update(hierarchy_references(child, source, "extends"))
        elif child.type == "super_interfaces":
            relation = "extends" if kind == "interface" else "implements"
            refs.update(hierarchy_references(child, source, relation))
    for name in parameter_types(declaration.child_by_field_name("parameters"), source):
        refs.add(("field", name))
    body = declaration.child_by_field_name("body")
    if body is not None:
        for member in body.named_children:
            if member.type in {"field_declaration", "constant_declaration"}:
                for name in type_names(source, member.child_by_field_name("type")):
                    refs.add(("field", name))
            elif member.type in {"method_declaration", "constructor_declaration", "annotation_type_element_declaration"}:
                member_parameters = type_parameters(member, source)
                for name in type_names(source, member.child_by_field_name("type")):
                    if name not in member_parameters:
                        refs.add(("signature", name))
                for name in parameter_types(member.child_by_field_name("parameters"), source):
                    if name not in member_parameters:
                        refs.add(("signature", name))
                for child in member.named_children:
                    if child.type == "throws":
                        for name in type_names(source, child):
                            refs.add(("signature", name))
    parameters = type_parameters(declaration, source)
    return sorted(
        ((relation, name) for relation, name in refs if name not in parameters),
        key=lambda item: (RELATION_ORDER[item[0]], item[1]),
    )


def members(body):
    for child in body.named_children:
        if child.type == "enum_body_declarations":
            yield from members(child)
        else:
            yield child


def body_references(declaration, source):
    body = declaration.child_by_field_name("body")
    if body is None:
        return set()
    class_parameters = type_parameters(declaration, source)
    names = set()
    for member in members(body):
        if member.type in TYPE_KINDS:
            continue
        excluded = class_parameters | type_parameters(member, source)
        stack = [member]
        while stack:
            node = stack.pop()
            if node.type in TYPE_KINDS:
                continue
            if node.type in {"type_identifier", "scoped_type_identifier"}:
                names.update(name for name in type_names(source, node) if name not in excluded)
                continue
            receiver = None
            if node.type in RECEIVER_OWNERS:
                receiver = node.child_by_field_name("object")
            elif node.type == "method_reference" and node.named_children:
                receiver = node.named_children[0]
            if receiver is not None and receiver.type == "identifier":
                name = source_text(source, receiver)
                if name[:1].isupper() and name not in excluded:
                    names.add(name)
            stack.extend(node.named_children)
    return names


def resolve_reference(
    name, current_name, current_path, source, root, package, imports, wildcard_imports, index
):
    first, _, remainder = name.partition(".")
    groups = []
    if first in imports:
        groups.append([imports[first] + ("." + remainder if remainder else "")])
    elif name[0].islower() and "." in name:
        groups.append([name])
    else:
        enclosing = current_name
        while enclosing != package and enclosing:
            groups.append([enclosing + "." + name])
            enclosing = enclosing.rpartition(".")[0]
        groups.append([(package + "." if package else "") + name])
        groups.append([wildcard + "." + name for wildcard in wildcard_imports])
    for group in groups:
        matches = []
        for qualified_name in dict.fromkeys(group):
            paths = candidate_paths(qualified_name, index)
            if not paths and find_declaration(root, source, package, qualified_name) is not None:
                paths = [current_path]
            for path in paths:
                if path == current_path and find_declaration(root, source, package, qualified_name) is None:
                    continue
                matches.append((qualified_name, path))
        if len(matches) == 1:
            qualified_name, path = matches[0]
            return qualified_name, path, None
        if len(matches) > 1:
            return None, None, "ambiguous"
    return None, None, "external_or_missing"


def inspect(project_root, entry, max_classes):
    index = file_index(java_files(project_root))
    entry_paths = candidate_paths(entry, index)
    if not entry_paths:
        raise ValueError(f"Entry type not found: {entry}")
    if len(entry_paths) > 1:
        candidates = ", ".join(str(path.relative_to(project_root)) for path in entry_paths)
        raise ValueError(f"Entry type is ambiguous: {entry} ({candidates})")

    parser = Parser(Language(tree_sitter_java.language()))
    cache = {}
    pending = deque([(entry, entry_paths[0])])
    queued = {entry}
    selected = {}
    resolved = set()
    unresolved = set()
    invalid = set()
    body_found = set()

    while pending and len(selected) < max_classes:
        qualified_name, path = pending.popleft()
        if path not in cache and len(cache) >= max_classes:
            pending.appendleft((qualified_name, path))
            break
        source, root, package, imports, wildcard_imports = load_file(path, parser, cache)
        declaration = find_declaration(root, source, package, qualified_name)
        if declaration is None:
            if qualified_name == entry:
                raise ValueError(f"Type {qualified_name} was not declared in {path}")
            invalid.add(qualified_name)
            for reference in tuple(resolved):
                if reference[2] == qualified_name:
                    unresolved.add((reference[0], reference[1], qualified_name, "not_declared"))
                    resolved.remove(reference)
            continue
        selected[qualified_name] = {
            "name": qualified_name,
            "kind": TYPE_KINDS[declaration.type],
            "path": path.relative_to(project_root).as_posix(),
        }
        for relation, name in references(declaration, source):
            target, target_path, reason = resolve_reference(
                name, qualified_name, path, source, root, package, imports, wildcard_imports, index
            )
            if target is None:
                unresolved.add((qualified_name, relation, name, reason))
                continue
            if target in invalid:
                unresolved.add((qualified_name, relation, name, "not_declared"))
                continue
            resolved.add((qualified_name, relation, target))
            if target not in queued:
                queued.add(target)
                pending.append((target, target_path))
        for name in body_references(declaration, source):
            target, target_path, _ = resolve_reference(
                name, qualified_name, path, source, root, package, imports, wildcard_imports, index
            )
            if target is not None and target != qualified_name:
                body_found.add((qualified_name, target, target_path.relative_to(project_root).as_posix()))

    relations = [
        {"from": source, "to": target, "kind": relation}
        for source, relation, target in sorted(resolved)
        if target in selected
    ]
    unresolved_items = sorted(unresolved)
    omitted = {target for _, _, target in resolved if target not in selected}
    body_items = sorted(
        item for item in body_found if item[1] not in selected and item[1] not in invalid
    )
    return {
        "entry": entry,
        "max_classes": max_classes,
        "classes": list(selected.values()),
        "relations": relations,
        "unresolved_references": [
            {"from": source, "kind": relation, "type": name, "reason": reason}
            for source, relation, name, reason in unresolved_items[:UNRESOLVED_SAMPLE_LIMIT]
        ],
        "unresolved_reference_count": len(unresolved_items),
        "omitted_class_count": len(omitted),
        "truncated": bool(pending),
        "body_references": [
            {"from": source, "type": target, "path": target_path}
            for source, target, target_path in body_items[:UNRESOLVED_SAMPLE_LIMIT]
        ],
        "body_reference_count": len(body_items),
    }


def main():
    argument_parser = argparse.ArgumentParser(description=__doc__)
    argument_parser.add_argument("--project-root", required=True, type=Path, help="Java project root")
    argument_parser.add_argument("--entry", required=True, help="Fully qualified entry type")
    argument_parser.add_argument("--max-classes", type=int, default=30, help="Maximum emitted types (default: 30)")
    args = argument_parser.parse_args()
    if not args.project_root.is_dir():
        argument_parser.error(f"Project root is not a directory: {args.project_root}")
    if args.max_classes < 1:
        argument_parser.error("--max-classes must be a positive integer")
    if not args.entry or any(not part for part in args.entry.split(".")):
        argument_parser.error("--entry must be a fully qualified type name")
    try:
        result = inspect(args.project_root.resolve(), args.entry, args.max_classes)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(f"inspect_java_classes: {error}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
