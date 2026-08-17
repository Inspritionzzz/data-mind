(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();

  var chartEtf = echarts.init(document.getElementById('chart-etf'), null, { renderer: 'svg' });

  chartEtf.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      formatter: function(params) {
        var p = params[0];
        return p.name + '<br/>配置权重: <b>' + p.value + '%</b>';
      }
    },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '6%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: muted, fontSize: 12, formatter: '{value}%' },
      axisLine: { lineStyle: { color: '#dee2e6' } },
      splitLine: { lineStyle: { color: '#dee2e6' } },
      name: '配置权重 (%)',
      nameTextStyle: { color: muted, fontSize: 12 },
      max: 30
    },
    yAxis: {
      type: 'category',
      axisLabel: { color: ink, fontSize: 12 },
      axisLine: { lineStyle: { color: '#dee2e6' } },
      data: [
        '芯片ETF', '科创芯片ETF', '半导体设备ETF', '科创200ETF',
        '黄金ETF', '黄金股ETF',
        '稀有金属ETF', '有色金属ETF', '新能源车ETF',
        '恒生科技ETF', '港股通互联网ETF',
        '创新药ETF', '医疗ETF',
        '红利低波ETF', '沪深300ETF'
      ]
    },
    series: [{
      type: 'bar',
      data: [
        { value: 8, itemStyle: { color: accent } },
        { value: 7, itemStyle: { color: accent } },
        { value: 5, itemStyle: { color: accent } },
        { value: 5, itemStyle: { color: accent } },
        { value: 10, itemStyle: { color: accent2 } },
        { value: 5, itemStyle: { color: accent2 } },
        { value: 6, itemStyle: { color: accent + 'cc' } },
        { value: 5, itemStyle: { color: accent + 'cc' } },
        { value: 4, itemStyle: { color: accent + 'cc' } },
        { value: 6, itemStyle: { color: '#2e7d32' } },
        { value: 4, itemStyle: { color: '#2e7d32' } },
        { value: 5, itemStyle: { color: accent + '66' } },
        { value: 5, itemStyle: { color: accent + '66' } },
        { value: 8, itemStyle: { color: muted } },
        { value: 7, itemStyle: { color: muted } }
      ],
      barWidth: 16,
      label: {
        show: true,
        position: 'right',
        color: ink,
        fontSize: 11,
        formatter: '{c}%'
      }
    }]
  });
  window.addEventListener('resize', function() { chartEtf.resize(); });
})();