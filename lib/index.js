// dsh-project-kit — host half.
//
// Registers the two skills shipped in skills/ with the harness skill registry,
// so the same repository can be installed either as plain files under
// <dshHome>/skills or as a bundle through the plugin manager.
//
// Registered skills are runtime skills: they carry the invocation policy the
// bundle declares and outrank a same-name copy in the user skill root, so an
// installation never depends on the file layout of ~/.dsh/skills.

import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'dsh-project-kit'
export const inject = ['skills']

const SKILL_ROOT = fileURLToPath(new URL('../skills/', import.meta.url))

/** Strip the optional matching quotes a YAML scalar may carry. */
function unquote(value) {
  const text = value.trim()
  if (text.length > 1 && (text[0] === '"' || text[0] === "'") && text.at(-1) === text[0]) {
    return text.slice(1, -1)
  }
  return text
}

/**
 * Split one SKILL.md into its flat frontmatter fields and its body.
 * Only the scalar subset the bundle ships is supported; anything richer would
 * be better read through the filesystem provider instead of this module.
 */
function parseSkillDocument(text, file) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text)
  if (match === null) throw new Error(`${file} has no YAML frontmatter`)

  const fields = {}
  for (const line of match[1].split(/\r?\n/)) {
    const trimmed = line.trim()
    if (trimmed === '' || trimmed.startsWith('#')) continue
    const at = line.indexOf(':')
    if (at === -1) continue
    fields[line.slice(0, at).trim()] = unquote(line.slice(at + 1))
  }
  return { fields, body: text.slice(match[0].length).trimStart() }
}

/**
 * Register every directory bundle under skills/ as a runtime skill.
 * @param ctx - Cordis context carrying the `skills` registry.
 */
export function apply(ctx) {
  for (const entry of readdirSync(SKILL_ROOT, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue

    const directory = join(SKILL_ROOT, entry.name)
    const file = join(directory, 'SKILL.md')
    const { fields, body } = parseSkillDocument(readFileSync(file, 'utf8'), file)

    ctx.skills.register({
      name: fields.name ?? entry.name,
      description: fields.description ?? '',
      ...(fields.whenToUse === undefined ? {} : { whenToUse: fields.whenToUse }),
      content: body,
      source: name,
      path: file,
      resourceBase: { kind: 'directory', path: directory },
      invocation: { modelInvocable: true, userInvocable: true },
    })
  }
}
