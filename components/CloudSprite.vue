<template>
  <!-- 可复用云朵 SVG：软 3D 奶油云（渐变主体 + 顶部高光 + 柔和投影），颜色走 CSS 变量 -->
  <svg class="cloud-sprite" viewBox="0 0 200 110" aria-hidden="true">
    <!-- 底部柔和投影 -->
    <ellipse cx="100" cy="103" rx="88" ry="9" fill="var(--cloud-drop)" />
    <!-- 主体：圆叠加 + 底部连接 -->
    <g fill="var(--cloud-fill)">
      <circle cx="45" cy="68" r="24" />
      <circle cx="86" cy="52" r="36" />
      <circle cx="108" cy="62" r="26" />
      <circle cx="132" cy="70" r="22" />
      <rect x="32" y="52" width="130" height="28" rx="14" />
    </g>
    <!-- 顶部高光（软奶油感） -->
    <ellipse cx="72" cy="42" rx="34" ry="13" fill="var(--cloud-shine)" />
  </svg>
</template>
