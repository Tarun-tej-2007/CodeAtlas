const fs = require('fs');
const files = [
  'client/components/auth/auth-field.tsx',
  'client/components/auth/password-requirements.tsx',
  'client/components/auth/password-strength.tsx'
];
files.forEach(f => {
  if (fs.existsSync(f)) {
    let c = fs.readFileSync(f, 'utf8');
    c = c.split('\\' + '`').join('`');
    c = c.split('\\' + '$').join('$');
    fs.writeFileSync(f, c);
  }
});
