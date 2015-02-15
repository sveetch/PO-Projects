(function( $ ) {

// Function to check if an element is in the viewport
// http://stackoverflow.com/a/7557433/5628
function isElementInViewport (el) {
    //special bonus for those using jQuery
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
    );
}

/*
 * jQuery plugin to apply a fixed position on an element when it's outside of 
 * the viewport
 */
$.fn.fixed_menu = function(options) {
    return this.each(function() {
        var $menu = $(this),
            settings = $.extend({
                'container_selector': '.catalog-messages-form',
                'arrival_selector': '#fixed-stats-menu',
                'clone_css': {
                    'display': 'none', // Important, else the clone is visible since loading
                    'position': 'fixed',
                    'top': 0,
                    'left': 0,
                    'right': 0,
                    'z-index': '9000'
                }
            }, options),
            // Container element where the clone will be prepend to
            $container = $(settings.container_selector),
            // Forged wrapper to contain the clone
            $clone_wrapper = $('<div>').css(settings.clone_css).addClass("fixed-menu-wrapper"),
            // The clone
            $cloned = $menu.clone();

        // Mark the original element
        $(this).addClass("fixed-menu-original");
        
        // Fill some things onto the clone
        $cloned.addClass("fixed-menu-clone");
        $cloned.removeAttr("id");
        //$cloned.css({'position': 'fixed', 'top': 0, 'z-index': '9000'});
        
        // Put the clone into its wrapper
        $cloned.appendTo($clone_wrapper);
        
        // Prepend the wrapper with its clone into the container
        $clone_wrapper.prependTo($container);
        
        // Handler called each time the viewport is loaded or "moving" (scroll, etc..)
        function onVisibilityChange(menu, clone) {
            return function () {
                if(isElementInViewport(menu)){
                    clone.hide();
                } else {
                    clone.show();
                }
            }
        }
        
        // Watch for menu visibility
        var handler = onVisibilityChange($menu, $clone_wrapper);
        $(window).on('DOMContentLoaded load resize scroll', handler);
    });
};

/*
 * jQuery plugin to mark a translation row as fuzzy or enabled when their 
 * input is changed (like with a checkbox click on itself or its label)
 */
$.fn.mark_fuzzy_translation = function(options) {
    return this.each(function() {
        var $input = $(this),
            settings = $.extend({
                'status_fuzzy_label': "Fuzzy",
                'status_enabled_label': "Enabled"
            }, options);
            
        $input.change(function(e) {
            var $row;
            if ( $(this).is( ":checked" ) ){
                $row = $(this).parents(".message-row");
                $row.removeClass('enabled').addClass('fuzzy');
                $row.find(".holder.checkbox label").text(settings.status_fuzzy_label);
            } else {
                $row = $(this).parents(".message-row");
                $row.removeClass('fuzzy').addClass('enabled');
                $row.find(".holder.checkbox label").text(settings.status_enabled_label);
            }
            return true;
        });
    });
};

/*
 * jQuery plugin to watch inputs for changes to update translation stats
 */
$.fn.update_translation_stats = function(options) {
    return this.each(function() {
        var $input = $(this),
            settings = $.extend({
                'fuzzy_count_selector': 'input',
                'empty_count_selector': 'textarea',
                'fuzzy_value_selector': '.po-trans-stats-fuzzy span.value',
                'empty_value_selector': '.po-trans-stats-empty span.value'
            }, options);
            
        $input.change(function(e) {
            var $this = $(this),
                empty_count = 0;
                
            // Count fuzzy checked input and update its stats
            $(settings.fuzzy_value_selector).text($(settings.fuzzy_count_selector+':checked').length);
            
            // Count empty textarea and update its stats
            $(settings.empty_count_selector).each(function() {
                if(!$(this).val()){
                    empty_count += 1;
                }
            });
            $(settings.empty_value_selector).text(empty_count);
            
            return true;
        });
    });
};

}( jQuery ));