/* Navbar for mobile */
let openbtn = document.getElementsByClassName('menu-sandwich');
if (typeof openbtn[0] !== "undefined" ) {
    openbtn[0].addEventListener('click', function openNav() {
        open = document.getElementById("mySidenav").style.width = "250px";
    });
}
let close = document.getElementsByClassName('closebtn');
if (typeof close[0] !== "undefined" ) {
    close[0].addEventListener('click', function closeNav() {
        document.getElementById("mySidenav").style.width = "0";
    });
}


let fitbtn = document.getElementById("fit");
let columns = document.getElementsByClassName('column');
let curfit = document.getElementsByTagName("img");
let len = curfit.length;
let savebtn = document.getElementById("save");
let clearbtn = document.getElementById("clear");


/* Remember style change */
targets = document.getElementsByClassName('column');
/* function will write attributes to local storage*/
function getsize(target) {
    id = target.id;
    width = target.style.width;
    height = target.style.height;
    localStorage.setItem(id,"width: " + width +"; height: " + height +";");
}
function record() {
    for (each of targets){
    getsize(each)}
}

function loadstyles() {
    for (each of targets){
        id = each.id;
        values = localStorage.getItem(id);
        each.style = values;
    }
}
function clear() {
    localStorage.clear();
    location.reload();
}
document.addEventListener("DOMContentLoaded", loadstyles);


/* Fit button */

if (fitbtn !== null ) {
    fitbtn.addEventListener("click", function () {
        for (let i = 0; i < len; i++) {
            if (curfit[i].classList.contains("img")) {
                curfit[i].classList.remove("img");
                columns[i].classList.remove('resize');
            } else {
                curfit[i].classList.add("img");
                columns[i].classList.add('resize');
            }
        }
        if (savebtn.classList.contains('hide')){
            savebtn.classList.remove('hide');
            clearbtn.classList.remove('hide');
        } else {
            savebtn.classList.add('hide');
            clearbtn.classList.add('hide');
        }
    });
}


if (savebtn !==null){
    savebtn.addEventListener('click', record)
}
if (clearbtn !==null){
    clearbtn.addEventListener('click', clear)
}
/* Show add images*/
let add = document.getElementById("add");
let uploadform = document.getElementById("upload");

function closeForm() {
  if (uploadform.classList.contains("hide")) {
      uploadform.classList.remove( "hide")} else {
      uploadform.classList.add("hide");
  }
}
if (add !==null){
    add.addEventListener("click", closeForm);
}
/* hide --- option and choose first other instead*/
let option = document.getElementsByTagName('option');
let select_form = document.getElementById('id_moodboard');
if (typeof option[0] !== "undefined" ){
    if (option[0].innerText === ("---------")) {
        option[0].classList.add('hide');
        select_form.options.selectedIndex = 1;
        document.removeEventListener('mouseup', getsize);
    }
 }
/* rotate */
let rotatebtns = document.getElementsByClassName('rotate');
let rotateAngle = 90;
let images = document.getElementsByTagName('img');

for (let i=0; i<rotatebtns.length; i++){
    rotatebtns[i].addEventListener("click", function () {
        images[i].setAttribute("style", "transform: rotate(" + rotateAngle + "deg)");
        rotateAngle = rotateAngle + 90;
    })
}
/* hide board */
let hider = document.getElementsByClassName("hider");
let mdbToHide = document.getElementsByClassName('pictures');
let revealer = document.getElementsByClassName('revealer');
if (typeof hider[0] !== "undefined" ){
    for (let x=0; x<hider.length; x++){
        hider[x].addEventListener("click",function () {
            mdbToHide[x].classList.add("hide");
            hider[x].classList.add("hide");
            revealer[x].classList.remove("hide");
            revealer[x].addEventListener("click", function () {
                mdbToHide[x].classList.remove("hide");
                hider[x].classList.remove("hide");
                revealer[x].classList.add("hide");
            })
        } )
    }
}
/* get csrf token*/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/*
const request = new Request(
    'https://themoodboard.herokuapp.com/myboards/ordered',
    {headers: {'X-CSRFToken': csrftoken}}
);


*/