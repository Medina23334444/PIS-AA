
const book = document.getElementById("book");
const menu = document.getElementById("menu");
const barraLateral = document.getElementById("barra-lateral");
const spans = document.querySelectorAll("span");

menu.addEventListener("click", ()=>{
    barraLateral.classList.toggle("max-barra-lateral")
})

book.addEventListener("click", ()=>{
    barraLateral.classList.toggle("mini-barra-lateral");
   spans.forEach((span)=>
   span.classList.toggle("oculto"))
})



