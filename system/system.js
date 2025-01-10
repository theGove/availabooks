//new and improved
function init(){
    getToc() 
    
    // Set a function onscroll - this will activate if the user scrolls
    //dims the buttons when the user scrolls
    window.onscroll = function() {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        //document.documentElement.scrollTop+document.documentElement.clientHeight,document.documentElement.scrollHeight
        if (scrollTop < 20 || Math.abs((scrollTop + clientHeight)-scrollHeight)<5) {
            dimButtons('bright')
            dimHeader('bright')
        } else {
            dimButtons('dim')
            dimHeader('dim')
        }
        //hideMenu()
    }

    window.addEventListener('hashchange', function() {
        if(window.location.hash){
            scroll_to(window.location.hash.substring(1))
        } else {
            showSection(1)
        }
        
      });

    window.addEventListener('resize', setTopMargin);
    setTopMargin()
    console.log("hash", window.location.hash)
    if(window.location.hash){
        scroll_to(window.location.hash.substring(1))
    }else{
        showSection(1)
    }
}

function setTopMargin(){
    const header = document.getElementsByTagName("header")[0]
    const margin = header.offsetHeight 
    for(section of document.querySelectorAll('.chapter-section')){
        section.style.marginTop = (margin * 1.1) + 'px'
    }
    // tag("menu").style.marginTop = margin + 'px'
    // console.log("margin", margin + 'px')

}

function scroll_to(id, recordHash=true){
    // Scroll to the specified element, being sure it is visible
    console.log("scrollTo", id)
    hideMenu()
    let element = tag(id)
    while (!element.className.includes('chapter-section')) {
        element = element.parentElement;
    }

    showSection(element.id.split('-')[1],false)
    
    if(id !== element.id){
      // this is not a section, scroll to it  
      tag(id).scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    if(recordHash){
        window.location.hash = '#' + id
    }

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
function showSection(section, recordHash=true){
    // section can be a number or 'next' or 'prior' or 'all'
    let sectionsToHide = []
    let sectionToShow = 1
    let currentlyShowing = 0
    let buttonNavigatgion = false
    const sections = document.querySelectorAll('.chapter-section')

    if(sections.length === 0){return}

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
        buttonNavigatgion = true
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
        if(recordHash){
          window.location.hash = 'section-' + sectionToShow
        }
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
    tag('menu').style.left= '0'
    // console.log("menuWidth",menuWidth)
    // if(tag("menu-button").innerHTML === "close"){
    //     tag("menu-button").innerHTML="menu"
    //     tag('menu').style.left= `-${menuWidth+10}px`
    // }else{
    //     tag("menu-button").innerHTML="close"
    //     tag('menu').style.left= '0'
    // }    
    
}

function hideMenu(){
    let menuWidth=tag('menu').offsetWidth
    tag('menu').style.left= `-${menuWidth+10}px`    
}

async function getToc(){
  let url=window.location  
  path = url.pathname.split("/")
  path.pop()
  path.push("toc.html")
  path.unshift(url.origin)
  url=path.join("/")
  console.log ("url", url)


  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const text = await response.text();
    const toc=JSON.parse(text.split("<!--postBegin-->")[1].split("<!--postEnd-->")[0])
    console.log(toc)
    const  html=[]
    for(const chapter of toc.chapters){

        if(chapter.sections){
            html.push("<details>")
            getChaptSections(chapter, html)
            html.push("</details>")
        }else{                
            html.push(chapter.text)
        }        
    }
    tag("toc").innerHTML=html.join("\n")


   


  } catch (error) {
    console.error(error.message);
  }


}

function getChaptSections(obj, html) { 
    html.push("<summary>")
    html.push(`<span>${obj.id.split("-").join(".")}: </span><span><a href="${newPathName(window.location.pathname,obj.id)}#heading-${obj.id}">${obj.text}</a></span>`)
    html.push("</summary>")
    for(const child of obj.sections){
        if(child.sections){
            html.push('<div class="toc-section-container"><details>')
            getChaptSections(child, html)
            html.push("</details></div>")
        }else{                
            html.push('<div class="toc-text-container">')
            html.push(`<a href="${newPathName(window.location.pathname,child.id)}#heading-${child.id}"><span>${child.id.split("-").join(".")}: </span><span>${child.text}</a></span>`)
            html.push("</div>")
        }

    }
    function newPathName(path, id){
        const pathArray=path.split("/")        
        fileArray = pathArray[pathArray.length-1].split(".")
        currentChapter=fileArray[0]
        linkChapter = id.split("-").shift()
        console.log("currentChapter",currentChapter,"linkChapter",linkChapter )
        if(linkChapter===currentChapter){
            // link to a place on the same page
            return ""
        }else{
            //link to a place on a different page
            fileArray[0] = linkChapter
            pathArray[pathArray.length-1] = fileArray.join(".")
            return pathArray.join("/")
        }

        
    }
}


