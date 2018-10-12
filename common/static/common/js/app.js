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
    var len = $('.goods-transfer-row').length;
    $('<div/>', {
               'class' : 'goods-transfer-row', 'id' : 'row' + len, html: GetGoodsRowHtml()
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
    var len = $('.goods-transfer-row').length;
    var $html = $('.goods-transfer-row-template').clone();

    goods_row_fields = [
        'form-FORMID-category',
        'form-FORMID-goods',
        'form-FORMID-measure',
        'form-FORMID-quantity',
        'form-FORMID-price',
        'form-FORMID-generate_inv_numbers',
        'form-FORMID-inv_numbers',
    ];

    for (var i = goods_row_fields.length - 1; i >= 0; i--) {
        search_statement = '[name=' + goods_row_fields[i] + ']'
        field = $html.find(search_statement)[0];

        field.name = field.name.replace('FORMID', len);
    }

    if (len >= 1) {
        close_button = $html.find('[id=deleteRow]')[0]
        close_button.id='deleteRow' + len;
        close_button.classList.remove('hidden');
    }

    $('input[name=form-TOTAL_FORMS]').val(len + 1);

    return $html.html();
}