import type { Unit } from "../types";

interface SidebarProps {
  units: Unit[];
  unitId: string;
  sessionId: string;
  selectedUnit?: Unit;
  onUnitChange: (unitId: string) => void;
  onSessionChange: (sessionId: string) => void;
}

export function Sidebar({
  units,
  unitId,
  sessionId,
  selectedUnit,
  onUnitChange,
  onSessionChange,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <h2>Tenant context</h2>

      <label className="field">
        <span>Unit</span>
        <select value={unitId} onChange={(event) => onUnitChange(event.target.value)}>
          {units.map((unit) => (
            <option key={unit.id} value={unit.id}>
              {unit.id} ({unit.property_name} #{unit.label})
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Session ID</span>
        <input
          type="text"
          value={sessionId}
          onChange={(event) => onSessionChange(event.target.value)}
        />
      </label>

      {selectedUnit ? (
        <div className="context-card">
          <p>
            <strong>Property:</strong> {selectedUnit.property_name}
          </p>
          <p>
            <strong>Unit:</strong> {selectedUnit.label}
          </p>
        </div>
      ) : null}

      <div className="prompts">
        <h3>Try asking</h3>
        <ul>
          <li>How much notice do I need to renew?</li>
          <li>What is the pet policy?</li>
          <li>Kitchen sink is leaking badly</li>
          <li>There is mold in the bathroom</li>
        </ul>
      </div>
    </aside>
  );
}
