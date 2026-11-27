// static/js/navbar.js

document.addEventListener('DOMContentLoaded', function () {
  const megaMenus = document.querySelectorAll('.mega-menu');

  megaMenus.forEach(function(menuWrapper) {
    const dropdownPanel = menuWrapper.querySelector('.mega-menu-content');
    const menuArrow = menuWrapper.querySelector('.dropdown-toggle');
    // 获取包裹文字和箭头的父容器
    const triggerArea = menuWrapper.querySelector('.d-flex.align-items-center');

    if (triggerArea && dropdownPanel && menuArrow) {
      
      // 让整个区域显示小手光标，提示用户可点击
      triggerArea.style.cursor = 'pointer';

      // 1. 点击文字或箭头所在的整个区域，切换菜单显示/隐藏
      triggerArea.addEventListener('click', function (e) {
        // 【关键】阻止默认跳转行为，让点击只触发菜单展开
        e.preventDefault(); 
        e.stopPropagation(); 
        
        const isOpen = dropdownPanel.style.display === 'block';
        
        // 关闭其他已打开的菜单
        document.querySelectorAll('.mega-menu-content').forEach(function(panel) {
            panel.style.display = 'none';
        });
        document.querySelectorAll('.mega-menu .dropdown-toggle').forEach(function(arrow) {
            arrow.classList.remove('rotate-arrow');
        });

        // 切换当前菜单的状态
        if (!isOpen) {
            dropdownPanel.style.display = 'block';
            menuArrow.classList.add('rotate-arrow');
        }
      });

      // 2. 点击页面其他空白处，关闭所有菜单
      document.addEventListener('click', function (e) {
        if (!dropdownPanel.contains(e.target) && !triggerArea.contains(e.target)) {
          if (dropdownPanel.style.display === 'block') {
            dropdownPanel.style.display = 'none';
            menuArrow.classList.remove('rotate-arrow');
          }
        }
      });
    }
  });
});