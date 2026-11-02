export const modules = [
  { id: 'materials', name: 'Materiały' },
  { id: 'loads', name: 'Obciążenia' },
  { id: 'combinations', name: 'Kombinacje obciążeń' },
  { id: 'resistance', name: 'Nośność i stateczność' },
  { id: 'connections', name: 'Połączenia' },
] as const;
export type ModuleId = typeof modules[number]['id'];
