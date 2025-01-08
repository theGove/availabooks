//new and improved
function init(){

    showSection(1)
    // Set a function onscroll - this will activate if the user scrolls
    //dims the buttons when the user scrolls
    window.onscroll = function() {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop < 20 || scrollTop + clientHeight >= scrollHeight) {
            dimButtons('bright')
            dimHeader('bright')
        } else {
            dimButtons('dim')
            dimHeader('dim')
        }
        hideMenu()
    }

    window.addEventListener('resize', setTopMargin);
    setTopMargin()
    console.log("hash", window.location.hash)
    if(window.location.hash){
        scroll_to(window.location.hash.substring(1))
    }
}

function setTopMargin(){
    const header = document.getElementsByTagName("header")[0]
    const margin = header.offsetHeight 
    for(section of document.querySelectorAll('.chapter-section')){
        section.style.marginTop = (margin * 1.1) + 'px'
    }
    tag("menu").style.marginTop = margin + 'px'
    console.log("margin", margin + 'px')

}

function scroll_to(id){
    // Scroll to the specified element, being sure it is visible
    console.log("scrollTo", id)
    let element = tag(id)
    while (!element.className.includes('chapter-section')) {
        element = element.parentElement;
    }

    showSection(element.id.split('-')[1])
    

    tag(id).scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function tag(id){
    return document.getElementById(id)
}

function dimButtons(brightOrDim){
    for(const button of document.querySelectorAll('.nav')){
        if(brightOrDim === 'bright'){
            button.classList.remove("dim-button")
        } else {
            // Dim the button
            button.classList.add("dim-button")
        }
    }
}
function dimHeader(brightOrDim){
    for(const header of document.getElementsByTagName("header")){
        if(brightOrDim === 'bright'){
            header.classList.remove("dim-header")
        } else {
            // Dim the button
            header.classList.add("dim-header")
        }
    }
}
function showSection(section){
    // section can be a number or 'next' or 'prior' or 'all'
    let sectionsToHide = []
    let sectionToShow = 1
    let currentlyShowing = 0
    const sections = document.querySelectorAll('.chapter-section')

    if(section === 'all'){
        for(const elem of sections){
            elem.style.display = 'block'
        }
        return
    }

    


    // find the section to hide
    for(const elem of sections){
        if(elem.style.display !== 'none'){
            currentlyShowing = parseInt(elem.id.split('-')[1])
            console.log("currentlyShowing", currentlyShowing)
            sectionsToHide.push(currentlyShowing)
        }
    }

    // find section to show
    if(isNaN(section)){
        // section s string and should be 'next' or 'prior'
        if(section === 'next'){
            sectionToShow = currentlyShowing + 1
        }else{
            //section === 'prior'
            sectionToShow = currentlyShowing - 1
        }
    }else{
        // section numeric
        sectionToShow = section
    }

    // prevents sectionToShow from being out of bounds
    if (isNaN(sectionToShow)){return}

    if(sectionToShow < 1){
        const components = window.location.pathname.split('/')
        priorChapter = parseInt(components[components.length - 1].split('.')[0]) - 1
        if (priorChapter < 1){
            sectionToShow = 1
        }else{
            window.location.href = priorChapter + '.html'
            return
        }

    }else if(sectionToShow > sections.length){
        // navigate to next chapter
        // needs to be updated to work with TOC, for now, it will guess the chapter number
        const components = window.location.pathname.split('/')
        nextChapter = parseInt(components[components.length - 1].split('.')[0]) + 1
        window.location.href = nextChapter + '.html'
        return 
    }

    for(const sectionNumber of sectionsToHide ){
        tag('section-' + sectionNumber).style.display = 'none'
    }

    tag('section-' + sectionToShow).style.display = 'block'  
    
    if(sectionToShow===1){
        window.scrollTo(0,0)
    }else{
        window.scrollTo(0,25)
        window.location.hash = 'section-' + sectionToShow
    }
    
}

function navigate(direction){
    // used for the navigation buttons. direction is 'next' or 'prior'
    if(direction === 'next'){
        showSection('next')
    } else{
        // direction === 'prior'
        showSection('prior')
    }
    
}

function showMenu(){
    // show the menu
    console.log("showing menu")
    
    let menuWidth=tag('menu').offsetWidth

    if (menuWidth === 0){
        tag('menu').style.display = 'block'
        menuWidth=tag('menu').offsetWidth
    }   

    console.log("menuWidth",menuWidth)
    if(tag("menu-button").innerHTML === "close"){
        tag("menu-button").innerHTML="menu"
        tag('menu').style.left= `-${menuWidth+10}px`
    }else{
        tag("menu-button").innerHTML="close"
        tag('menu').style.left= '0'
    }    
    
}

function hideMenu(){
    let menuWidth=tag('menu').offsetWidth
    tag("menu-button").innerHTML="menu"
    tag('menu').style.left= `-${menuWidth+10}px`
    
}