import { ModelProvider } from "../utils/types";

interface Props {
  selected: ModelProvider;
  onChange: (provider: ModelProvider) => void;
}

export default function ModelSelector({ selected, onChange }: Props): JSX.Element {
  return (
    <select value={selected} onChange={(event) => onChange(event.target.value as ModelProvider)}>
      <option value="gemini">Gemini</option>
      <option value="groq">Groq</option>
    </select>
  );
}
