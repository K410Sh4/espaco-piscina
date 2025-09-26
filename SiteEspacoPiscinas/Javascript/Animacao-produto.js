const telaInicio = document.querySelector(`.wellcome h1`);
telaInicio.innerText = `Conheça nossos produtos !!`; 
telaInicio.style.color = `rgb(0, 0, 0)`;
telaInicio.style.backgroundColor = `rgb(255, 255, 255)`;
telaInicio.style.padding = `2vw`;
telaInicio.style.borderRadius = `1vw`;
telaInicio.style.boxShadow = `0 0 1vw black`;

const produtos = document.querySelectorAll(`.product-image img`);
produtos.forEach((produtos) => {
    produtos.style.boxShadow = `0 0 0.5vw cyan`;
});





    