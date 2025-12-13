const API="http://localhost:5000/tasks";
const t=localStorage.getItem("token");

function add(){
 fetch(API,{method:"POST",
 headers:{"Content-Type":"application/json","Authorization":"Bearer "+t},
 body:JSON.stringify({title:title.value,due_date:due.value,priority:priority.value})
 }).then(load);
}

function load(){
 fetch(API,{headers:{Authorization:"Bearer "+t}})
 .then(r=>r.json()).then(d=>{
  list.innerHTML="";
  d.forEach(x=>{
   list.innerHTML+=`<li>${x.title} ${x.status}
   <button onclick="done(${x.id})">✔</button></li>`;
  })
 })
}

function done(id){
 fetch(`${API}/${id}/complete`,{method:"PUT",headers:{Authorization:"Bearer "+t}})
 .then(load)
}

load();
