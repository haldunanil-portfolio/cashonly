function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

function titleCase(str) {
  return str.toLowerCase().split(' ').map(function(word) {
    return word.replace(word[0], word[0].toUpperCase());
  }).join(' ');
};

function animateNext(elem, animating) {
  if(animating) return false;
  animating = true;

  current_fs = elem.parent();
  next_fs = elem.parent().next();

  //show the next fieldset
  next_fs.show();
  // hide the current fieldset
  current_fs.animate({opacity: 0}, {
    step: function(now, mx) {
      // as the opacity of current_fs goes down to 0, it gets stored it 'now'
      // begin by scaling current_fs down to 80%
      scale = 1 - (1 - now) * 0.2;
      // next, bring in next_fs from the right side
      left = (now * 50)+'%';
      // next up, increase opacity of next_fs to 1 as it moves in
      opacity = 1 - now;
      current_fs.css({'transform': 'scale('+scale+')'});
      next_fs.css({'left': left, 'opacity': opacity});
    },
    duration: 800,
    complete: function() {
      current_fs.hide();
      animating = false;
    },
    easing: 'easeInOutBack'
  });

  return {
    animating: animating,
    current_fs: current_fs,
    next_fs: next_fs
  };
};

function animatePrev(elem, animating) {
  if(animating) return false;
  animating = true;

  current_fs = elem.parent();
  previous_fs = elem.parent().prev();

  //show the previous fieldset
  previous_fs.show();
  // hide the current fieldset
  current_fs.animate({opacity: 0}, {
    step: function(now, mx) {
      // as the opacity of current_fs goes down to 0, it gets stored it 'now'
      // begin by scaling previous_fs from 80% to 100%
      scale = 0.8 + (1 - now) * 0.2;
      // next, bring in next_fs from the right(50%) - from 0%
      left = ((1 - now) * 50)+'%';
      // next up, increase opacity of next_fs to 1 as it moves in
      opacity = 1 - now;
      current_fs.css({'left': left});
      previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
    },
    duration: 800,
    complete: function() {
      current_fs.hide();
      animating = false;
    },
    easing: 'easeInOutBack'
  });

  return {
    animating: animating,
    current_fs: current_fs,
    previous_fs: previous_fs
  };
};
