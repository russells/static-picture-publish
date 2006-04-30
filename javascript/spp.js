// Javascript for static-picture-publish.


function select_all_images()
{
  var cb
  var n
  var cbs = document.getElementsByName("image-select")
  for (n=0; n<cbs.length; n++) {
    cb = cbs[n]
    cb.checked = true
  }
}

function unselect_all_images()
{
  var cb
  var n
  var cbs = document.getElementsByName("image-select")
  for (n=0; n<cbs.length; n++) {
    cb = cbs[n]
    cb.checked = false
  }
}

function download_selected_images()
{
  var cb
  var n
  var cbs = document.getElementsByName("image-select")
  var s = ""
  var files = new Array()
  for (n=0; n<cbs.length; n++) {
    cb = cbs[n]
    if (cb.checked) {
      files[files.length] = cb.value
    }
  }
  if (files.length == 0) {
    alert("Nothing selected, downloading no files.")
  } else {
    s = "If this worked, I would be downloading "
    // alert("files.length = "+files.length)
    for (n=0; n<files.length; n++) {
      if (n > 2)
        break
      s = s + files[n]
      if (n < files.length-1)
        s = s + ", "
    }
    if (files.length > 3) {
      s = s + " ..."
    }
    alert(s)
  }
  if (files.length > 0) {
    alert("opening "+files[0])
    //open(files[0])
  } else {
    alert("no files?")
  }
}


// arch-tag: 028baf8c-9845-4d04-b9a8-e1b074fdb262
