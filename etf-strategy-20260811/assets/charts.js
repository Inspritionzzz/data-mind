(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var red = '#d32f2f';
  var green = '#2e7d32';

  // --- Chart: 板块涨跌对比 ---
  var chartSector = echarts.init(document.getElementById('chart-sector'), null, { renderer: 'svg' });
  chartSector.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: muted, fontSize: 12, formatter: '{value}%' },
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule } },
      name: '涨跌幅 (%)',
      nameTextStyle: { color: muted, fontSize: 12 }
    },
    yAxis: {
      type: 'category',
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: rule } },
      data: ['锂矿', 'PEEK材料', 'CPO', 'PCB', '新能源车', '稀有金属', '算力硬件', '储能', '医药', '白酒', '银行', '黄金', '影视']
    },
    series: [{
      type: 'bar',
      data: [
        { value: 8.50, itemStyle: { color: red } },
        { value: 5.20, itemStyle: { color: red } },
        { value: 3.80, itemStyle: { color: red } },
        { value: 3.40, itemStyle: { color: red } },
        { value: 3.00, itemStyle: { color: red } },
        { value: 2.80, itemStyle: { color: red } },
        { value: 2.50, itemStyle: { color: red } },
        { value: 1.80, itemStyle: { color: red } },
        { value: 0.60, itemStyle: { color: red } },
        { value: 0.30, itemStyle: { color: red } },
        { value: -0.50, itemStyle: { color: green } },
        { value: -3.50, itemStyle: { color: green } },
        { value: -1.20, itemStyle: { color: green } }
      ],
      barWidth: 16,
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontSize: 11,
        formatter: function(p) { return (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '%'; }
      }
    }]
  });
  window.addEventListener('resize', function() { chartSector.resize(); });

  // --- Chart: 模拟盘ETF方向预期 ---
  var chartEtf = echarts.init(document.getElementById('chart-etf'), null, { renderer: 'svg' });

  chartEtf.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true
    },
    legend: {
      bottom: 0,
      textStyle: { color: muted, fontSize: 11 }
    },
    grid: { left: '3%', right: '4%', bottom: '14%', top: '6%', containLabel: true },
    xAxis: {
      type: 'category',
      axisLabel: { color: ink, fontSize: 10, rotate: 35 },
      axisLine: { lineStyle: { color: rule } },
      data: ['稀有金属', '新能源车', '有色金属', '电池', '通信/5G', '科创芯片', '半导体设备', '创新药', '储能/新能源', '红利低波', '黄金']
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: muted, fontSize: 12, formatter: '{value}' },
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule } },
      name: '模拟盘配置权重 (%)',
      nameTextStyle: { color: muted, fontSize: 12 }
    },
    series: [{
      name: '今日建议',
      type: 'bar',
      data: [
        { value: 15, itemStyle: { color: accent } },
        { value: 10, itemStyle: { color: accent } },
        { value: 5, itemStyle: { color: accent } },
        { value: 5, itemStyle: { color: accent } },
        { value: 8, itemStyle: { color: accent2 } },
        { value: 7, itemStyle: { color: accent2 } },
        { value: 5, itemStyle: { color: accent2 } },
        { value: 8, itemStyle: { color: accent + '99' } },
        { value: 7, itemStyle: { color: accent + '99' } },
        { value: 20, itemStyle: { color: muted } },
        { value: 0, itemStyle: { color: '#e0e0e0' } }
      ],
      barWidth: 18,
      label: { show: true, position: 'top', color: ink, fontSize: 11, formatter: '{c}%' }
    }]
  });
  window.addEventListener('resize', function() { chartEtf.resize(); });

})();