// Wait for the DOM to be ready (all elements printed on page regardless if loaded or not)
$(function() {

    // Bind a click event to anything with the class "toggle-nav"
    $('.toggle-nav').click(function() {

          // Toggle the Body Class "show-nav"
          $('div.navmenu').toggleClass('show-nav');
          $('div.mobile-menu-toggle').toggleClass('hide-mobile-menu-toggle');

          // Deactivate the default behavior of going to the next page on click
          return false;

    });
});
