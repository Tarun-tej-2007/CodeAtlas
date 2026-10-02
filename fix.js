const fs = require('fs');
const files = [
  'client/components/activity/activity-header.tsx',
  'client/components/activity/activity-overview.tsx',
  'client/components/activity/activity-timeline.tsx',
  'client/components/activity/activity-details.tsx',
  'client/components/activity/activity-statistics.tsx',
  'client/components/activity/activity-summary.tsx',
  'client/components/activity/activity-export.tsx',
  'client/app/activity/page.tsx',
  'client/lib/mock-data/activity.ts',
  'client/types/activity-ui.ts'
];
files.forEach(f => {
  if (fs.existsSync(f)) {
    let c = fs.readFileSync(f, 'utf8');
    c = c.split('\\' + '`').join('`');
    c = c.split('\\' + '$').join('$');
    fs.writeFileSync(f, c);
  }
});
