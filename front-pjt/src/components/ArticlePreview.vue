<script setup>
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { defineProps, computed } from "vue";
import { RouterLink } from "vue-router";

const props = defineProps({
  news: {
    type: Object,
    required: true
  },
  to: {
    type: String,
    default: null
  }
});

const { formatDate } = useDate();
const hasInteraction = computed(() => {
  return (
    "article_interaction" in props.news && !!props.news.article_interaction
  );
});
</script>

<template>
  <RouterLink
    v-if="props.to"
    :to="props.to"
  >
    <ContentBox>
      <div class="top">
        <h1>{{ props.news.title }}</h1>
      </div>
      <div class="bottom">
        <div>
          <StateButton type="tag" size="sm">{{
            props.news.writer
          }}</StateButton>
          {{ formatDate(new Date(props.news.write_date)) }}
        </div>

        <div v-if="hasInteraction" class="bottom__icons">
          <div v-if="hasInteraction">
            ❤️ {{ props.news.article_interaction?.likes }}
          </div>
          <div>
            👀 {{ props.news.views ?? 0 }}
          </div>
        </div>
      </div>
    </ContentBox>
  </RouterLink>

  <div v-else-if="news && news.title">
     <ContentBox>
      <div class="top">
        <h1>{{ props.news.title }}</h1>
      </div>
      <div class="bottom">
        <div>
          <StateButton type="tag" size="sm">{{
            props.news.writer
          }}</StateButton>
          {{ formatDate(new Date(props.news.write_date)) }}
        </div>

        <div v-if="hasInteraction" class="bottom__icons">
          <div v-if="hasInteraction">
            ❤️ {{ props.news.article_interaction?.likes }}
          </div>
          <div>
            👀 {{ props.news.views ?? 0 }}
          </div>
        </div>
      </div>
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.top {
  h1 {
    font-size: 15px;
  }
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
.bottom {
  display: flex;
  align-items: baseline;
  gap: 10px;
  justify-content: space-between;

  &__icons {
    display: flex;
    gap: 10px;
  }
}

a {
  display: block;
  text-decoration: none;
  color: inherit;
}
</style>
