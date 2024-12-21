//new and improved
function init(){
    // Set a function onscroll - this will activate if the user scrolls
    //dims the buttons when the user scrolls
    window.onscroll = function() {
        // Set the height to check for
        var appear = 20
        if (window.pageYOffset >= appear) {
            dimButtons('bright')
        } else {
            dimButtons('dim')
        }
    }
}

function tag(id){
    return document.getElementById(id)
}

function dimButtons(brightOrDim){
    for(const button of document.querySelectorAll('.nav')){
        if(brightOrDim === 'bright'){
            button.classList.add("extra-class")
        } else {
            // Dim the button
            button.classList.remove("extra-class")
        }
    }
}

function showSection(section){
    // section can be a number or 'next' or 'prior' or 'all'
    let sectionsToHide = []
    let sectionToShow = 1
    let currentlyShowing = 0
    const sections = document.querySelectorAll('.section')

    if(section === 'all'){
        for(const elem of sections){
            elem.style.display = 'block'
        }
        return
    }

    


    // find the section to hide
    for(const elem of sections){
        if(elem.style.display === 'block'){
            currentlyShowing = parseInt(elem.id.split('-')[1])
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
    if(sectionToShow < 1){
        sectionToShow = 1

    }else if(sectionToShow > sections.length){
        sectionToShow = sections.length
    }

    for(const sectionNumber of sectionsToHide ){
        tag('section-' + sectionNumber).style.display = 'none'
    }

    tag('section-' + sectionToShow).style.display = 'block'        
}

function navigate(direction){
    // used for the navigation buttons. direction is 'next' or 'prior'
    if(direction === 'next'){
        showSection('next')
    } else{
        // direction === 'prior'
        showSection('prior')
    }
    window.scrollTo(0,0)
}