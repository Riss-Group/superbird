/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import VariantMixin from "@website_sale/js/sale_variant_mixin";
var registry = publicWidget.registry;
var timer;

publicWidget.registry.WebsiteSale.include({
    'selector': '#wrapwrap',
    _onChangeCombination: function(ev, $parent, combination) {
        this._super.apply(this, arguments);
        var current_date = combination.current_date
        var start_date = combination.start_date
        var end_date = combination.end_date
        var msg = combination.offer_msg || ''
        if (end_date != parseInt($(".end_date").val())) {
            if (combination.is_offer && combination.current_date !== 'undefined') {
                var append_date = "<div class='timer_input'><input type='hidden' class='current_date' value=" + current_date + "></input><input type='hidden' class='start_date' value=" + start_date + "></input><input type='hidden' class='end_date' value=" + end_date + "></input><div class='te_offer_timer_msg_div'><h6 class='te_offer_timer_prod fw-normal'>" + msg + "</p></h6></div></div>"
                $(".timer_data").html(append_date);
                $(".current_date").trigger('change');
            } else {
                $("#timer_portion_content_ept").removeClass("d-none");
                var append_date = "<div class='timer_input'><input type='hidden' class='current_date' value=" + 0 + "></input><input type='hidden' class='start_date' value=" + 0 + "></input><input type='hidden' class='end_date' value=" + 0 + "></input></div>"
                $(".timer_data").html(append_date);
                $(".current_date").trigger('change');
            }
        }
        $(".js_sku_div").html('N/A');
        if (combination.sku_details) {
            $(".js_sku_div").html(combination.sku_details);
        }
        if (combination.price_table_details) {
                $('.te_price_table').removeClass('d-none').html(combination.price_table_details)
        }
        $(".js_product .te_discount, .js_product .te_discount_before").addClass('d-none');
        $(".js_product .te_discount, .js_product .te_percentage").hide()
        if (combination.has_discounted_price) {
            $(".js_product .te_discount, .js_product .te_discount_before").removeClass('d-none');
            var difference = combination.list_price - combination.price;
            var discount = difference * 100 / combination.list_price;
            if (discount > 0) {
                $(".js_product .te_discount_before .oe_currency_value").html(difference.toFixed(2));
                $(".js_product .te_discount .te_percentage .percent_val").html(discount.toFixed(2));
                $(".js_product .te_discount, .js_product .te_percentage").show()
            }
        }
    },
});

publicWidget.registry.timer_data = publicWidget.Widget.extend({
    selector: ".timer_data",
    events: {
        'change .current_date': 'initOfferTimer',
    },
    start: function() {
        this.redrow();
    },
    stop: function() {
        this.clean();
    },
    redrow: function(debug) {
        this.clean(debug);
        this.build(debug);
    },
    clean: function(debug) {
        this.$target.empty();
    },
    build: function(debug) {},
    initOfferTimer: function() {
        /* This method is called for initialize and update the offer timer in at product page*/
        var product_offer;
        clearInterval(timer);
        var count_start_date = parseInt($(".start_date").val());
        var count_end_date = parseInt($(".end_date").val());
        var current_date_time = parseInt($(".current_date").val());
        $("#timer_portion_content_ept").addClass("d-none");
        timer = setInterval(function() {
            if (count_start_date <= current_date_time && count_end_date >= current_date_time) {
                var duration = count_end_date - current_date_time;
                product_offer = true;
            } else {
                product_offer = false;
            }
            var seconds = "00";
            var days = "00";
            var minutes = "00";
            var hours = "00";
            if (duration > 0) {
                var days = Math.floor(duration / (1000 * 60 * 60 * 24));
                var hours = Math.floor((duration % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((duration % (1000 * 60)) / 1000);

                if ((seconds + '').length == 1) {
                    seconds = "0" + seconds;
                }
                if ((days + '').length == 1) {
                    days = "0" + days;
                }
                if ((hours + '').length == 1) {
                    hours = "0" + hours;
                }
                if ((minutes + '').length == 1) {
                    minutes = "0" + minutes;
                }
                if (product_offer == true) {
                    $("#days").text(days);
                    $("#hours").text(hours);
                    $("#minutes").text(minutes);
                    $("#seconds").text(seconds);
                    $(".te_offer_timer_prod").css("display", "block");
                    $("#timer_portion_content_ept").removeClass("d-none");
                }
            }
            current_date_time += 1000
        }, 1000);
    }
});

