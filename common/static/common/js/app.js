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

function addNewRow() {
    var len = $('.goods-row').length;
    $('<div/>', {
               'class' : 'goods-row', 'id' : 'row' + len, html: GetGoodsRowHtml()
     }).hide().appendTo('#goodsRowsContainer').slideDown('fast');

    close_button = $('#deleteRow' + len);
    close_button.on('click', function() {
        removeGoodsRow(len);
    });
}

function removeGoodsRow(rowId) {
    row = $('#row' + rowId);
    row.slideUp('fast', function() {
        row.remove();
    });
}

function GetGoodsRowHtml()
{
    var len = $('.goods-row').length;
    var $html = $('.goods-row-template').clone();
    $html.find('[name=category]')[0].name='category' + len;
    $html.find('[name=goods]')[0].name='goods' + len;
    $html.find('[name=measure]')[0].name='measure' + len;
    $html.find('[name=gen_inv_numbers]')[0].name='gen_inv_numbers' + len;
    $html.find('[id=quantity]')[0].id='quantity' + len;
    $html.find('[id=price]')[0].id='price' + len;

    if (len >= 1) {
        close_button = $html.find('[id=deleteRow]')[0]
        close_button.id='deleteRow' + len;
        close_button.classList.remove('hidden');
    }
    return $html.html();
}