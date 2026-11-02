import { expect, it } from 'vitest';
import fixture from '../fixtures/project.json';
import { createProjectDraft } from '../../src/domain/project';
import { modules } from '../../src/domain/modules';
it('wczytuje przykładowy projekt i udostępnia odrębne moduły', () => { expect(createProjectDraft(fixture.name).name).toBe('Przykładowy dach'); expect(new Set(modules.map(m => m.id)).size).toBe(5); });
