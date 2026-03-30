// JavaScript for toggling the dropdown menu
document.addEventListener("DOMContentLoaded", function () {
    const navToggle = document.querySelector(".nav-toggle");
    const navLinks = document.querySelector(".nav-links");

    navToggle.addEventListener("click", function () {
        navLinks.classList.toggle("active");
    });
//

// ниже валидация ввода на фронте
//document.addEventListener("DOMContentLoaded", () => {
//
//    console.log("DOM ready");
//
//    const form = document.querySelector("form");
//    const inputs = document.querySelectorAll(".input-player");
//
//    console.log("inputs:", inputs);
//
//    const regex = /^[A-Za-zА-Яа-яЁё\s-]+$/;
//
//    function validateInput(input) {
//        console.log("validating:", input.value);
//
//        const value = input.value.trim();
//        const errorDiv = input.parentElement.querySelector(".error-message");
//
//        let error = "";
//
//        if (value.length === 0) {
//            error = "Поле обязательно";
//        } else if (value.length < 2) {
//            error = "Минимум 2 символа";
//        } else if (value.length > 20) {
//            error = "Максимум 20 символов";
//        } else if (!regex.test(value)) {
//            error = "Только буквы, пробелы и дефисы";
//        }
//
//        if (error) {
//            input.style.border = "2px solid red";
//            errorDiv.textContent = error;
//            return false;
//        } else {
//            input.style.border = "2px solid green";
//            errorDiv.textContent = "";
//            return true;
//        }
//    }
//
//    inputs.forEach(input => {
//        input.addEventListener("input", () => validateInput(input));
//    });
//
//    form.addEventListener("submit", (e) => {
//        let isValid = true;
//
//        inputs.forEach(input => {
//            if (!validateInput(input)) isValid = false;
//        });
//
//        if (!isValid) e.preventDefault();
//    });
//
//});