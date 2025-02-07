<script setup>
    import Card from './Card.vue'
</script>

<template>

    <p class="indent-tiny bold uppercase p-header-adjust-large">Dine opgaver</p>
    <div class="card-list">
        <Card id="card1"
            title="Gennemfør IT-sikkerhedskursus"
            header="Lær om informationssikkerhed, GDPR og meget mere!"
            description="Du skal gennemføre Randers Kommune's IT-sikkerhedskursus. Det er dit eget ansvar at gennemføre kurset."
            :deadline="new Date(new Date().getTime() + 8 * 60 * 60 * 1000)"
            responsible=""
            :booking="new Date(new Date().getTime() + 6 * 60 * 60 * 1000)"
            image="https://www.teknologisk.dk/_/media/67761&w=1460&h=808&r=cover&_filename=67761_7-gode-rr%C3%A5d-til-IT-sikkerhed.jpg"
            color="4c4980"
            link=""
            isComplete="false" />
    </div><!-- /card-list -->

</template>