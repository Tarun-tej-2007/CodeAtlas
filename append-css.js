const fs = require('fs');

const css = \`

/* --- React Flow CodeAtlas Dark Theme Overrides --- */

html body .react-flow__background {
  background-color: #080D18;
}

html body .react-flow__controls {
  background-color: #0F1726;
  border: 1px solid #1E293B;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;
}

html body .react-flow__controls-button {
  background-color: #0F1726;
  border: none;
  border-bottom: 1px solid #1E293B;
  fill: #94A3B8;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  padding: 0;
  margin: 0;
}

html body .react-flow__controls-button:last-child {
  border-bottom: none;
}

html body .react-flow__controls-button:hover {
  background-color: #17233A;
  fill: #3B82F6;
}

html body .react-flow__controls-button:focus,
html body .react-flow__controls-button:active {
  background-color: #17233A;
  outline: 2px solid #3B82F6;
  outline-offset: -2px;
}

html body .react-flow__controls-button svg {
  max-width: 14px;
  max-height: 14px;
}

html body .react-flow__minimap {
  background-color: #0B1220;
  border: 1px solid #1E293B;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3);
  width: 200px;
  height: 140px;
  overflow: hidden;
}

html body .react-flow__minimap svg {
  width: 100%;
  height: 100%;
  display: block;
}

html body .react-flow__minimap-mask {
  fill: rgba(8, 13, 24, 0.7);
  stroke: #1E293B;
  stroke-width: 1px;
}

html body .react-flow__attribution {
  background: rgba(15, 23, 38, 0.7);
  color: #64748B;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
}

html body .react-flow__attribution a {
  color: #64748B;
  text-decoration: none;
}

html body .react-flow__attribution a:hover {
  color: #94A3B8;
}
\`;

fs.appendFileSync('client/app/globals.css', css);
console.log("Appended styles successfully.");
