<script setup>
    import { ref } from 'vue'
    var cardRef = ref(null)

    const expandCard = () => {
        cardRef.value.classList.toggle('expand-content')
    }

    const returnTimeLeft = (deadline) => {
        const now = new Date()
        const diff = deadline - now
        const hours = Math.floor(diff / 1000 / 60 / 60)
        return hours
    }

    const returnFormattedDate = (date) => {
        const d = new Date(date)
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit' }) + ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
    }

    defineProps({
        title: {
            type: String,
            required: true
        },
        header:
        {
            type: String,
            default: ''
        },
        description: {
            type: String,
            default: ''
        },
        deadline: {
            type: Date
        },
        responsible: {
            type: String
        },
        booking: {
            type: Date
        },
        image: {
            type: String,
            default: ''
        },
        color: {
            type: String,
            default: '000'
        },
        link: {
            type: String
        }
    })
</script>

<template>

    <div class="card expand-content" ref="cardRef">
        <div class="card-header pointer" @click="expandCard">
            <div class="card-icon">
                <div :style="`background-color: #`+ color +`;`">
                    <div>i</div>
                </div>
            </div>

            <div>
                <p class="card-title">
                    {{ title }}
                </p>
                <p class="card-subtitle">
                    {{ header }}
                </p>
            </div>

            <div class="card-separator"></div>

            <div class="card-image" :style="`background-image: url('`+ image +`');`">
                &nbsp;
            </div>
        </div>

        <div class="card-large-image" :style="`background-image: url('`+ image +`');`">
            &nbsp;
        </div>

        <div class="card-content">
            <div class="card-details">
                <div>
                    <div class="icon"><i class="fa-solid fa-clock"></i></div>
                    <div class="text">
                        <div class="small faded">Deadline</div>
                        <div>{{ deadline ? returnTimeLeft(deadline) + ' timer' : 'Ingen deadline' }}</div>
                    </div>
                </div>

                <div>
                    <div class="icon"><i class="fa-solid fa-user"></i></div>
                    <div class="text">
                        <div class="small faded">Ansvarlig</div>
                        <div>{{ responsible ? responsible : 'Ingen ansvarlig' }}</div>
                    </div>
                </div>

                <div>
                    <div class="icon"><i class="fa-solid fa-calendar"></i></div>
                    <div class="text">
                        <div class="small faded">Booking</div>
                        <div>{{booking ? returnFormattedDate(booking) : 'Ingen kalenderbooking'}}</div>
                    </div>
                </div>
            </div>

            <p>{{ description }}</p>

            <div class="buttons">
                <div class="button" v-if="link">Gå til kursus</div>
                <div class="button disabled">Markér gennemført</div>
            </div>
        </div>
    </div>

</template>