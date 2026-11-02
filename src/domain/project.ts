export interface ProjectDraft { name: string; }
export function createProjectDraft(name: string): ProjectDraft {
  const normalized = name.trim();
  if (!normalized) throw new Error('Podaj nazwę projektu.');
  return { name: normalized };
}
