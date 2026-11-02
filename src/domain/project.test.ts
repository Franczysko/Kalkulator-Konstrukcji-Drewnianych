import { describe, it, expect } from 'vitest';
import { createProjectDraft } from './project';
describe('szkic projektu', () => {
 it('normalizuje nazwę', () => expect(createProjectDraft('  Dach  ')).toEqual({ name: 'Dach' }));
 it.each(['', '   '])('odrzuca pustą nazwę %j', name => expect(() => createProjectDraft(name)).toThrow('Podaj nazwę projektu.'));
});
