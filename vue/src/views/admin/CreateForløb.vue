<script setup>
</script>

<template>
  <p class="indent-tiny bold uppercase p-header-adjust">Opret forløb</p>

  <div class="formContainer">
    <div class="inputContainer">
      <input type="text" id="name" name="name" placeholder=" " required>
      <label for="name" class="floating-label">Medarbejder</label>
    </div>
    <div class="inputContainer">
      <input type="text" id="admin" name="admin" placeholder=" " value="Låst værdi" class="locked" required disabled>
      <label for="admin" class="floating-label">Ansvarlig leder</label>
      <div class="icon"><i class="fa-solid fa-lock"></i></div>
    </div>
    <div class="inputContainer">
      <select id="department" name="department" required>
        <option value="" disabled selected hidden></option>
        <option value="HR">HR</option>
        <option value="IT">IT</option>
        <option value="Finance">Finance</option>
        <option value="Marketing">Marketing</option>
      </select>
      <label for="department" class="floating-label">Afdeling</label>
      <div class="icon nohover"><i class="fa-solid fa-caret-down"></i></div>
    </div>
  </div>
</template>

<style scoped>
  .formContainer {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .inputContainer {
    position: relative;
    display: flex;
    flex-direction: row;
    gap: 1rem;
  }
  .floating-label {
    position: absolute;
    top: 0.9rem;
    left: 0.8rem;
    pointer-events: none;
    transition: 0.2s ease all;
    color: #787878;
    font-size: 1em;
  }
  input[type=text], select {
    background-color: rgb(241, 237, 232);
    width: 100%;
    padding: 1.6rem 0.8rem 0.6rem 0.8rem;
    box-sizing: border-box;
    border-radius: 0.2rem;
    border: 0rem;
    transition-duration: 200ms;
  }
  select {
    appearance: none;
    padding-left: 0.55rem;
  }
  input[type=text]:focus, select:focus {
    outline:none;
    background-color: rgb(248, 246, 244);
  }
  input:disabled {
    background-color: rgb(230, 224, 216);
    color: #4b8049;
    font-weight: 600;
  }
  .icon {
    position: absolute;
    right: 0rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.2rem;
    padding: 1.1rem;
    height: 100%;
    transition: 150ms;
  }
  .icon:hover:not(.nohover) {
    color: #4b8049;
    cursor: pointer;
  }
  .icon.nohover {
    pointer-events: none;
  }
  @media only screen and (min-width: 768px) {
    .floating-label {
      top: 0.9rem;
      left: 0.8rem;
    }
    input[type=text], select  {
      width: 30rem;
    }
    .icon {
      right: auto;
      left: 27rem;
    }
  }

  input[type=text]:focus + .floating-label,
  input[type=text]:not(:placeholder-shown) + .floating-label,
  select:valid + .floating-label {
    top: 0.5rem;
    left: 0.8rem;
    color: #8b8b8b;
    font-size: 0.8em;
  }
</style>