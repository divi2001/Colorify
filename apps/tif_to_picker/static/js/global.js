document.querySelectorAll('.nav-sidebar').forEach(nav => {
  nav.addEventListener('click', () => {

    document.querySelectorAll('.nav-sidebar.active').forEach(item => item.classList.remove('active'));
    nav.classList.add('active');
  });
});

const range = document.querySelector('.custom-range');
range.addEventListener('input', function() {
  const value = (this.value - this.min) / (this.max - this.min) * 100;
  this.style.background = `linear-gradient(to right, #3C4CD1 ${value}%, #ddd ${value}%)`;
});


document.addEventListener("DOMContentLoaded", () => {
  const profileItems = document.querySelectorAll(".profile-item");

  profileItems.forEach(profileItem => {
      const popoverId = profileItem.getAttribute("data-popover-target");
      const popover = document.getElementById(popoverId);

      profileItem.addEventListener("click", (event) => {
          document.querySelectorAll(".popover").forEach(otherPopover => {
              if (!otherPopover.isEqualNode(popover)) {
                  otherPopover.classList.add("opacity-0", "scale-95");
                  setTimeout(() => {
                      otherPopover.classList.add("hidden");
                  }, 300); 
              }
          });

          if (popover.classList.contains("hidden")) {
              popover.classList.remove("hidden");
              setTimeout(() => {
                  popover.classList.remove("opacity-0", "scale-95");
              }, 10);
          } else {
              popover.classList.add("opacity-0", "scale-95");
              setTimeout(() => {
                  popover.classList.add("hidden");
              }, 300); 
          }
      });
  });

  document.addEventListener("click", (event) => {
      const isProfileClick = event.target.closest(".profile-item");
      const isPopoverClick = event.target.closest(".popover");

      if (!isProfileClick && !isPopoverClick) {
          document.querySelectorAll(".popover").forEach(popover => {
              popover.classList.add("opacity-0", "scale-95");
              setTimeout(() => {
                  popover.classList.add("hidden");
              }, 300);
          });
      }
  });

  document.querySelectorAll('.popover').forEach(popover => {
      popover.addEventListener('click', function(event) {
          event.stopPropagation(); 
      });
  });
});



  function showTab(tabIndex) {
      const buttons = document.querySelectorAll('.tab-button');
      const contents = document.querySelectorAll('.tab-content');

      buttons.forEach(button => button.classList.remove('active'));
      contents.forEach(content => content.classList.remove('active'));

      document.querySelectorAll('.tab-button')[tabIndex - 1].classList.add('active');
      document.getElementById('tab' + tabIndex).classList.add('active');
  }


  document.querySelectorAll('.collapse_btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const tabContent = btn.closest('.tab-content');
      tabContent.classList.remove('active');
    });
  });


  document.getElementById('notification-tab').addEventListener('click', function() {
    document.getElementById('notification-content').classList.remove('hidden');
    document.getElementById('help-content').classList.add('hidden');
    this.classList.add( 'active_header_tab' );
    document.getElementById('help-tab').classList.remove('active_header_tab');
  });

  document.getElementById('help-tab').addEventListener('click', function() {
    document.getElementById('help-content').classList.remove('hidden');
    document.getElementById('notification-content').classList.add('hidden');
    this.classList.add('active_header_tab');
    document.getElementById('notification-tab').classList.remove('active_header_tab');
  });


  const collapseButton = document.querySelector('.collapse_right_btn');
  const collapsibleDiv = document.getElementById('collapsibleDiv'); 
  const icon = collapseButton.querySelector('svg'); 

  collapseButton.addEventListener('click', function () {
    collapsibleDiv.classList.toggle('hidden');
    if (collapsibleDiv.classList.contains('hidden')) {
      icon.setAttribute('d', 'm12.14 8.753-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z'); // Right caret icon
    } else {
      icon.setAttribute('d', 'm3.86 7.247 5.482-4.796c.646-.566 1.658-.106 1.658.753v8.393a1 1 0 0 1-1.659.753l-5.48-4.796a1 1 0 0 1 0-1.506z'); // Down caret icon
    }
  });


document.querySelector('.upload_file_btn').addEventListener('click',()=>{
  document.querySelector('#upload_file').click()
})