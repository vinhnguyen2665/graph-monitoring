export function formatClientTime(val: string | number | Date | null | undefined): string {
  if (!val) return '-';
  try {
    let dateStr = String(val).trim();
    if (!dateStr) return '-';

    // If timestamp doesn't specify timezone, treat as UTC
    if (dateStr.includes('T') && !dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-')) {
      dateStr += 'Z';
    } else if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/.test(dateStr)) {
      dateStr = dateStr.replace(' ', 'T') + 'Z';
    }

    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(val);

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch {
    return String(val);
  }
}

export function formatClientTimeShort(val: string | number | Date | null | undefined): string {
  if (!val) return '-';
  try {
    let dateStr = String(val).trim();
    if (!dateStr) return '-';

    if (dateStr.includes('T') && !dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-')) {
      dateStr += 'Z';
    } else if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/.test(dateStr)) {
      dateStr = dateStr.replace(' ', 'T') + 'Z';
    }

    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(val);

    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');

    return `${hours}:${minutes}`;
  } catch {
    return String(val);
  }
}
