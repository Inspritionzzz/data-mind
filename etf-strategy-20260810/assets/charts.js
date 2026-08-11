(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var red = '#d32f2f';
  var green = '#2e7d32';

  // --- Chart: 板块涨跌分布 ---
  var chartSector = echarts.init(document.getElementById('chart-sector'), null, { renderer: 'svg' });
  chartSector.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      formatter: function(params) {
        var p = params[0];
        return p.name + '<br/>涨跌幅: <b>' + (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '%</b>';
      }
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
      data: [
        '酒店餐饮', '能源金属', '贵金属', '医疗服务', '白酒',
        '兵装重组', '养殖', '食品饮料', '电网设备', '有色金属',
        '医药', '旅游', '电力', '银行', '保险',
        '机器人', '元件', '半导体', 'AI PC', '通信设备', 'CPO'
      ]
    },
    series: [{
      type: 'bar',
      data: [
        { value: 4.22, itemStyle: { color: red } },
        { value: 3.85, itemStyle: { color: red } },
        { value: 3.60, itemStyle: { color: red } },
        { value: 3.20, itemStyle: { color: red } },
        { value: 2.80, itemStyle: { color: red } },
        { value: 2.50, itemStyle: { color: red } },
        { value: 2.10, itemStyle: { color: red } },
        { value: 1.80, itemStyle: { color: red } },
        { value: 1.40, itemStyle: { color: red } },
        { value: 1.10, itemStyle: { color: red } },
        { value: 0.80, itemStyle: { color: red } },
        { value: 0.12, itemStyle: { color: red } },
        { value: 0.05, itemStyle: { color: red } },
        { value: -0.15, itemStyle: { color: green } },
        { value: -0.35, itemStyle: { color: green } },
        { value: -0.45, itemStyle: { color: green } },
        { value: -0.52, itemStyle: { color: green } },
        { value: -0.63, itemStyle: { color: green } },
        { value: -0.70, itemStyle: { color: green } },
        { value: -0.85, itemStyle: { color: green } },
        { value: -1.15, itemStyle: { color: green } }
      ],
      barWidth: 16,
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontSize: 11,
        formatter: function(p) {
          return (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '%';
        }
      }
    }]
  });
  window.addEventListener('resize', function() { chartSector.resize(); });

  // --- Chart: 重点ETF涨跌幅 ---
  var chartEtf = echarts.init(document.getElementById('chart-etf'), null, { renderer: 'svg' });
  var etfColor = [accent, accent2, muted, accent + '99', accent2 + '99', accent + '66', accent2 + '66', accent + '44', accent2 + '44', muted + '99'];

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
    grid: { left: '3%', right: '4%', bottom: '12%', top: '6%', containLabel: true },
    xAxis: {
      type: 'category',
      axisLabel: { color: ink, fontSize: 10, rotate: 30 },
      axisLine: { lineStyle: { color: rule } },
      data: [
        '创业板综ETF', '科创半导体设备ETF', '半导体设备ETF', '养殖ETF',
        '黄金ETF', '食品饮料ETF', '医疗ETF', '军工ETF',
        '新能源ETF', 'AI人工智能ETF'
      ]
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: muted, fontSize: 12, formatter: '{value}%' },
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule } },
      name: '涨跌幅 (%)',
      nameTextStyle: { color: muted, fontSize: 12 }
    },
    series: [{
      type: 'bar',
      data: [
        { value: 19.77, itemStyle: { color: accent } },
        { value: 4.12, itemStyle: { color: accent2 } },
        { value: 3.77, itemStyle: { color: accent } },
        { value: 2.50, itemStyle: { color: accent2 } },
        { value: 2.30, itemStyle: { color: accent } },
        { value: 1.65, itemStyle: { color: accent2 } },
        { value: 0.90, itemStyle: { color: accent } },
        { value: 0.55, itemStyle: { color: accent2 } },
        { value: 0.35, itemStyle: { color: accent } },
        { value: -3.13, itemStyle: { color: muted } }
      ],
      barWidth: 22,
      label: {
        show: true,
        position: 'top',
        color: ink,
        fontSize: 11,
        formatter: function(p) {
          return (p.value >= 0 ? '+' : '') + p.value.toFixed(2) + '%';
        }
      }
    }]
  });
  window.addEventListener('resize', function() { chartEtf.resize(); });

})();