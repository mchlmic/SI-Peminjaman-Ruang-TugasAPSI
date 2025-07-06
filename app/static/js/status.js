function updateFileName(input) {
    var fileName = input.files[0].name;
    var label = input.closest('.custom-file').querySelector('.custom-file-label');
    label.innerHTML = fileName;
}

function toggleDeskripsi(button) {
    const container = button.parentElement;
    const deskripsiPenuh = container.querySelector('.deskripsi-penuh');
    const deskripsiPotong = container.querySelector('.deskripsi-potong');

    deskripsiPenuh.classList.toggle('d-none');
    deskripsiPotong.classList.toggle('d-none');
    button.innerText = button.innerText === 'Show More' ? 'Show Less' : 'Show More';
}