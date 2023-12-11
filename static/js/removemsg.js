const domItems = document.querySelectorAll('.msg')

const arrItems = Array.from(domItems)

setTimeout(() => {
  arrItems.forEach(item=>item.style.display = 'none')
},7000)

