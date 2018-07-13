$(document).foundation()

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function changeStorePlace(store_place_pk) {
    setCookie('store_place_pk', store_place_pk, 30);

    if (window.location.href.indexOf('/store/') != -1) {
        window.location.pathname = ('/store/' + store_place_pk)
    }
}

function resetGoodsFilter() {
    checked_categories = $('input[type="checkbox"][name="category"]:checked')

    for (i = 0; i < checked_categories.length; ++i) {
        checked_categories[i].checked = false;
    }

    in_stock_radio = $('#in_stock')
    in_stock_radio.click();

    document.filtersForm.submit();
}

function jumpToUrl(url) {
    document.location.href = document.location.protocol
    + '//'
    + document.location.host
    + url;
}

function prepareGoodsTable() {
    goods_rows = $('.goods-row');

    for (i = goods_rows.length - 1; i >= 0; i--) {
        goods_row = goods_rows[i];
        url = goods_row.getElementsByClassName('hidden-url')[0].innerText;

        goods_row.addEventListener("click", jumpToUrl.bind(null, url));
    }
}
