<template>
  <div class="registerFormDiv">
    <form @submit.prevent="this.registration">
      <DxForm ref="registerForm" :form-data="this.registerFormData">
        <DxGroupItem caption="Регистрация">
          <DxGroupItem>
            <DxSimpleItem data-field="login">
              <DxLabel text="Логин" />
              <DxRequiredRule message="Введите логин" />
            </DxSimpleItem>
            <DxSimpleItem data-field="password" :editor-options="this.passwordEditorOptions">
              <DxLabel text="Пароль" />
              <DxRequiredRule message="Введите пароль" />
            </DxSimpleItem>
            <DxSimpleItem data-field="mail" :editor-options="this.emailEditorOptions">
              <DxLabel text="Почта" />
              <DxRequiredRule message="Введите почту" />
              <DxEmailRule message="Неверный формат почты" />
              <DxAsyncRule
                :validation-callback="asyncValidation"
                message="Такая почта уже зарегистрирована"
              />
            </DxSimpleItem>
          </DxGroupItem>
          <DxButtonItem :button-options="this.enterButtonOptions" />
          <DxButtonItem :button-options="this.loginButtonOptions" />
        </DxGroupItem>
      </DxForm>
    </form>
  </div>
</template>

<script>
import DxForm, {
  DxGroupItem,
  DxRequiredRule,
  DxSimpleItem,
  DxLabel,
  DxButtonItem,
  DxEmailRule,
  DxAsyncRule
} from 'devextreme-vue/form'

import axios from 'axios'
import notify from 'devextreme/ui/notify'

export default {
  components: {
    DxForm,
    DxGroupItem,
    DxSimpleItem,
    DxRequiredRule,
    DxLabel,
    DxButtonItem,
    DxEmailRule,
    DxAsyncRule
  },
  data() {
    return {
      passwordEditorOptions: {
        mode: 'password'
      },
      emailEditorOptions: {
        mode: 'email'
      },
      enterButtonOptions: {
        text: 'Зарегистрироваться',
        type: 'default',
        width: '500px',
        useSubmitBehavior: true
      },
      loginButtonOptions: {
        text: 'Авторизация',
        type: 'default',
        width: '500px',
        onClick: this.login
      },
      registerFormData: {
        login: null,
        password: null
      }
    }
  },
  methods: {
    registration() {
      axios
        .post('/auth/sign-up', this.registerFormData)
        .then((res) => {
          this.$store.dispatch('authenticateUser', res.data.access_token)
          this.$router.push('/')
        })
        .catch((error) => {
          notify({ message: error.response.data.detail, type: 'error' }, { position: 'center' })
        })
    },
    login() {
      this.$router.push('/login')
    },
    async asyncValidation(params) {
      return axios.post(`/auth/mail-verification?mail=${params.value}`).then((res) => {
        return res.data
      })
    }
  }
}
</script>

<style scoped>
.registerFormDiv {
  margin: auto;
  width: 350px;
  margin-top: 15px;
  border: 1px solid #d1d1d1;
  padding: 15px;
}
</style>
