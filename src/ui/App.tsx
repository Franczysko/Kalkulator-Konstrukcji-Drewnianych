import { useState, type FormEvent } from 'react';
import { modules } from '../domain/modules';
import { createProjectDraft } from '../domain/project';
export function App() {
 const [name, setName] = useState('');
 const [message, setMessage] = useState('');
 function submit(event: FormEvent) { event.preventDefault(); try { setMessage(`Utworzono szkic: ${createProjectDraft(name).name}`); } catch (error) { setMessage((error as Error).message); } }
 return <main><p className="eyebrow">PRACOWNIA KONSTRUKCJI</p><h1>Kalkulator konstrukcji drewnianych</h1><p>Środowisko do rozwoju modułów obliczeniowych.</p><aside>Wersja przygotowawcza — moduły obliczeniowe nie są jeszcze zaimplementowane.</aside><section><h2>Nowy projekt</h2><form onSubmit={submit}><label htmlFor="name">Nazwa projektu</label><input id="name" value={name} onChange={event => setName(event.target.value)} /><button type="submit">Utwórz szkic</button></form><p role="status">{message}</p></section><section><h2>Planowane moduły</h2><ul>{modules.map(module => <li key={module.id}>{module.name}<span>W przygotowaniu</span></li>)}</ul></section></main>;
}
