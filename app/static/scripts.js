function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(
        function () {
            alert("リンクがクリップボードにコピーされました");
        },
        function (err) {
            alert("クリップボードにコピーできませんでした: " + err);
        }
    );
}

function toggleUser(userLink) {
    const userGroup = document.querySelector(`.userGroup[data-user="${userLink}"]`);
    if (userGroup.style.display === 'none') {
        userGroup.style.display = 'block';
    } else {
        userGroup.style.display = 'none';
    }
}
