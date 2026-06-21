export const formatCellValue = (value: unknown, columnKey?: string): string => {
  if (value === null || value === undefined || value === '') {
    return '-';
  }

  if (typeof value === 'boolean') {
    return value ? 'Sim' : 'Não';
  }

  // Se for data no formato YYYY-MM-DD (ex: 2026-03-01)
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-');
    return `${day}/${month}/${year}`;
  }

  if (typeof value === 'number') {
    const colLower = columnKey ? columnKey.toLowerCase() : '';
    
    // Se a coluna indicar porcentagem (ex: FG%, LL%, pct)
    const isPercentageColumn = 
      colLower.endsWith('_pct') || 
      colLower.includes('%') || 
      colLower === 'pct' || 
      colLower === 'win_pct' ||
      colLower === 'ap(%)';

    if (isPercentageColumn) {
      // Se a porcentagem vier como decimal menor ou igual a 1 (ex: 0.999), multiplicamos por 100
      // Mas se já vier como 99.9, mantemos.
      const displayVal = (value <= 1.0 && value > 0) ? value * 100 : value;
      return `${displayVal.toFixed(1)}%`;
    }

    // Formata floats para 1 casa decimal por padrão
    if (!Number.isInteger(value)) {
      return value.toFixed(1);
    }

    return value.toString();
  }

  return String(value);
};

export const formatShortDate = (dateStr?: string): string => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      // Tentar split simples se a data for inválida para o construtor nativo
      if (/^\d{4}-\d{2}-\d{2}/.test(dateStr)) {
        const [year, month, day] = dateStr.split('T')[0].split('-');
        return `${day}/${month}/${year}`;
      }
      return dateStr;
    }
    return date.toLocaleDateString('pt-BR');
  } catch {
    return dateStr;
  }
};
