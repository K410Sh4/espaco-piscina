const login = document.getElementsByClassName("part-left");
const cadastro= document.getElementsByClassName("part-right")
const logo = document.getElementsByClassName("topo");

let Entrar = false

function metodoLogin(){
    if (Entrar == false){
       cadastro[0].style.opacity= "0"
       login[0].style.opacity = "1"
       login[0].style.marginLeft = "0vw"
       cadastro[0].style.marginLeft = "-40vw"
       Entrar = true;
    }
    else {
        cadastro[0].style.opacity= "1"
        login[0].style.opacity = "0"
        login[0].style.marginLeft = "40vw"
        Entrar = false;
    }
};
logo[0].addEventListener('click', metodoLogin);
