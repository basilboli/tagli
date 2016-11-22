$(document).on("click", ".open-deleteModal", function () {
     var tagId = $(this).data('id');
     $(".modal-body #tagId").val( tagId );
});
window.setTimeout(function() { $(".alert-dismissable").alert('close'); }, 10000);