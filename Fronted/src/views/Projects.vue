<template>
  <div class="container-fluid">
    <div>
      <DxDataGrid
        id="dgProjects"
        ref="dgProjects"
        :column-hiding-enabled="false"
        :data-source="this.gridDataSource"
        :remote-operations="false"
        :row-Alternation-Enabled="true"
        :show-borders="true"
        :show-row-lines="true"
        :word-wrap-enabled="true"
        @key-down="KeyDown"
        @editing-start="editingStart"
      >
        <DxColumn alignment="center" header-cell-template="header-cell" type="buttons" width="150">
          <gridButton name="open" hint="Открыть проект" icon="panelleft" @click="openProject" />
          <gridButton name="edit" hint="Редактировать проект" />
          <gridButton name="delete" hint="Удалить проект" />
        </DxColumn>

        <template #header-cell>
          <DxButton hint="Добавить проект" @click="addButtonClick">Добавить проект</DxButton>
        </template>

        <DxColumn caption="Название проекта" data-field="name" />
        <DxColumn
          caption="Дата создания"
          data-field="create_date"
          alignment="left"
          :width="120"
          data-type="datetime"
          format="shortDate"
        />
        <DxColumn caption="Описание" data-field="description" />

        <DxGroupPanel :visible="false" />
        <DxGrouping :auto-expand-all="false" />
        <DxFilterRow :visible="false" />
        <DxHeaderFilter :visible="false" />
        <DxScrolling mode="standard" />

        <DxEditing :allow-deleting="true" :allow-updating="true" :use-icons="true" mode="popup">
          <gridPopup
            :show-title="true"
            title="Редактирование проекта"
            :width="1100"
            :height="700"
            :hide-on-outside-click="false"
            :show-close-button="false"
            :drag-enabled="false"
            position="center"
            :enable-body-scroll="false"
          >
            <DxToolbarItem
              toolbar="bottom"
              widget="dxButton"
              location="after"
              :options="this.successButtonOptions"
            ></DxToolbarItem>
            <DxToolbarItem
              toolbar="bottom"
              widget="dxButton"
              location="after"
              :options="this.cancelButtonOptions"
            ></DxToolbarItem>
          </gridPopup>
          <DxForm :col-count="1" :show-colon-after-label="true" :alignItemLabels="true">
            <DxItem>
              <table>
                <tr>
                  <td>
                    <DxTextBox
                      v-model:value="this.editRowValue.project_name"
                      label="Название проекта"
                      labelMode="static"
                      :maxLength="50"
                    >
                      <DxValidator>
                        <DxRequiredRule message="Введите название проекта" />
                      </DxValidator>
                    </DxTextBox>
                  </td>
                </tr>
                <tr>
                  <td>
                    <DxTextBox
                      v-model:value="this.editRowValue.description"
                      label="Описание"
                      labelMode="static"
                    >
                    </DxTextBox>
                  </td>
                </tr>
                <tr>
                  <td>
                    <FileUploader
                      id="fu1"
                      ref="fileUploader"
                      :options="{
                        text: 'Загрузить координаты',
                        url: this.uploadUrl
                      }"
                      :isNewProject="false"
                      @fUData="acceptFUData"
                    />
                  </td>
                  <DxTooltip
                    :hide-on-outside-click="false"
                    target="#fu1"
                    show-event="mouseenter"
                    hide-event="mouseleave"
                  >
                    <div class="hint">
                      Можно загрузить один файл формата .txt! Как нужно заполнять файл: <br />
                      1строка:Timestamp(если есть временные метки, иначе пусто),Название координат
                      1(Описание),Название координат 2(Описание),...<br />
                      2строка:Метка времени,Значение координаты 1, Значение координаты 2,...<br />
                      Длина меток и координат должна быть одинаковой, разделителем служит ','.<br />
                      Первый столбец временные метки, а каждый последующий координаты.<br />
                      Если не будет описания координат, не ставьте ().
                    </div>
                  </DxTooltip>
                </tr>
                <tr>
                  <td>
                    <DxDataGrid
                      id="dgTimeSeries"
                      ref="dgTimeSeries"
                      :column-hiding-enabled="false"
                      :data-source="this.gDsTimeSeries"
                      :remote-operations="false"
                      :row-Alternation-Enabled="true"
                      :show-borders="true"
                      :show-row-lines="true"
                      :word-wrap-enabled="true"
                      @key-down="KeyDown"
                      :height="250"
                    >
                      <DxColumn caption="Координаты" data-field="ts_name" />
                      <DxColumn caption="Длина" data-field="len" alignment="left" :width="120" />
                      <DxColumn caption="Описание" data-field="ts_description" />

                      <DxGroupPanel :visible="false" />
                      <DxGrouping :auto-expand-all="false" />
                      <DxFilterRow :visible="false" />
                      <DxHeaderFilter :visible="false" />
                      <DxScrolling mode="standard" />
                    </DxDataGrid>
                  </td>
                </tr>
              </table>
              <DxValidationSummary id="Summary"></DxValidationSummary>
            </DxItem>
          </DxForm>
        </DxEditing>
      </DxDataGrid>

      <DxPopup
        v-model:visible="popupForCreateProjectVisible"
        @showing="onShowingCreateProjectPopup"
        :show-title="true"
        title="Создание проекта"
        :width="1100"
        :height="650"
        :hide-on-outside-click="false"
        :show-close-button="false"
        :drag-enabled="false"
        position="center"
        :enable-body-scroll="false"
        content-template="popup-content"
        ref="CreateProjectPopup"
      >
        <template #popup-content>
          <CreateProjectPopup
            ref="CreateProjectTemplate"
            @popupCloseButtonClick="popupCloseButtonClick"
          />
        </template>
      </DxPopup>
    </div>

    <div class="row">
      <div class="col">
        <DxDataGrid
          id="dgPrCoordinates"
          ref="dgPrCoordinates"
          :column-hiding-enabled="false"
          :data-source="this.$store.state.tsColors"
          :remote-operations="false"
          :row-Alternation-Enabled="true"
          :show-borders="true"
          :show-row-lines="true"
          :word-wrap-enabled="true"
        >
          <DxColumn
            caption="Координата"
            data-field="num"
            alignment="left"
            :width="100"
            :allowEditing="false"
          />
          <DxColumn
            caption="Цвет"
            data-field="color"
            cell-template="cell-color"
            edit-cell-template="cell-edit-color"
          />
          <template #cell-color="{ data }">
            <DxColorBox :value="data.value" :show-drop-down-button="false" />
          </template>
          <template #cell-edit-color="{ data: cellInfo }">
            <DxColorBox
              v-model:value="cellInfo.value"
              apply-value-mode="instantly"
              :accept-custom-value="false"
              :showDropDownButton="true"
              :onValueChanged="(e) => cellInfo.setValue(e.value)"
              :closed="this.$store.dispatch('changeColorTs')"
            />
          </template>
          <DxGroupPanel :visible="false" />
          <DxGrouping :auto-expand-all="false" />
          <DxFilterRow :visible="false" />
          <DxHeaderFilter :visible="false" />
          <DxScrolling mode="standard" />

          <DxEditing :allow-updating="true" mode="cell" />
        </DxDataGrid>
      </div>
      <div class="col">
        <DxDataGrid
          id="dgPrPrimitives"
          ref="dgPrPrimitives"
          :column-hiding-enabled="false"
          :data-source="this.$store.state.prColors"
          :remote-operations="false"
          :row-Alternation-Enabled="true"
          :show-borders="true"
          :show-row-lines="true"
          :word-wrap-enabled="true"
        >
          <DxColumn
            caption="Примитив"
            data-field="num"
            alignment="left"
            :width="100"
            :allowEditing="false"
          />
          <DxColumn
            caption="Цвет"
            data-field="color"
            cell-template="cell-color"
            edit-cell-template="cell-edit-color"
          />
          <template #cell-color="{ data }">
            <DxColorBox :value="data.value" :show-drop-down-button="false" />
          </template>
          <template #cell-edit-color="{ data: cellInfo }">
            <DxColorBox
              v-model:value="cellInfo.value"
              apply-value-mode="instantly"
              :accept-custom-value="false"
              :showDropDownButton="true"
              :onValueChanged="(e) => cellInfo.setValue(e.value)"
              :closed="this.$store.dispatch('changeColorPr')"
            />
          </template>

          <DxGroupPanel :visible="false" />
          <DxGrouping :auto-expand-all="false" />
          <DxFilterRow :visible="false" />
          <DxHeaderFilter :visible="false" />
          <DxScrolling mode="standard" />

          <DxEditing :allow-updating="true" mode="cell" />
        </DxDataGrid>
      </div>
    </div>
  </div>
</template>

<script>
import {
  DxDataGrid,
  DxColumn,
  DxFilterRow,
  DxHeaderFilter,
  DxEditing,
  DxButton as gridButton,
  DxForm,
  DxGroupPanel,
  DxGrouping,
  DxScrolling,
  DxPopup as gridPopup
} from 'devextreme-vue/data-grid'
import DxButton from 'devextreme-vue/button'
import { DxTextBox } from 'devextreme-vue/text-box'
import { DxItem } from 'devextreme-vue/form'
import CustomStore from 'devextreme/data/custom_store'
import { DxValidator, DxRequiredRule } from 'devextreme-vue/validator'
import { DxValidationSummary } from 'devextreme-vue/validation-summary'
import notify from 'devextreme/ui/notify'
// import { confirm } from 'devextreme/ui/dialog'
// import DxValidationGroup from 'devextreme-vue/validation-group'
import axios from 'axios'
import { DxPopup } from 'devextreme-vue/popup'
import CreateProjectPopup from '@/components/CreateProjectPopup.vue'
import { DxToolbarItem } from 'devextreme-vue/popup'
import FileUploader from '@/components/FileUploader.vue'
import { DxTooltip } from 'devextreme-vue/tooltip'
import DxColorBox from 'devextreme-vue/color-box'
import ruMessages from 'devextreme/localization/messages/ru.json'
import { locale, loadMessages } from 'devextreme/localization'

export default {
  name: 'ProjectsView',
  components: {
    DxDataGrid,
    DxColumn,
    DxFilterRow,
    DxHeaderFilter,
    DxEditing,
    gridButton,
    DxForm,
    DxGroupPanel,
    DxGrouping,
    DxScrolling,
    DxItem,
    DxButton,
    DxValidator,
    DxValidationSummary,
    DxRequiredRule,
    // DxValidationGroup,
    DxPopup,
    DxTextBox,
    gridPopup,
    CreateProjectPopup,
    DxToolbarItem,
    FileUploader,
    DxTooltip,
    DxColorBox
  },
  data() {
    return {
      gridDataSource: new CustomStore({
        key: 'id',
        load: () => {
          return axios
            .get('/projects/get')
            .then((res) => {
              return res.data
            })
            .catch((error) => {
              console.error(error)
            })
        },
        remove: (key) => {
          return axios.delete(`/project/delete?id=${key}`).then((res) => {
            if (res == undefined || res.status != 200 || res.data != true)
              notify(
                { message: 'Не удалось удалить запись!', type: 'error', displayTime: 3000 },
                { position: 'center' }
              )
          })
        }
      }),
      popupForCreateProjectVisible: false,
      editRowValue: {},
      gDsTimeSeries: [],
      uploadUrl: '',
      projectId: '',
      successButtonOptions: {
        type: 'success',
        stylingMode: 'outlined',
        text: 'Сохранить',
        onClick: this.customSaveButtonClick
      },
      cancelButtonOptions: {
        type: 'danger',
        stylingMode: 'outlined',
        text: 'Отменить',
        onClick: this.customCancelButtonClick
      }
    }
  },
  created() {
    loadMessages(ruMessages)
    locale('ru-RU')
  },
  methods: {
    addButtonClick() {
      this.popupForCreateProjectVisible = true
    },
    KeyDown(e) {
      if (e.event.key == 'Enter') {
        e.event.preventDefault()
      }
    },
    customCancelButtonClick() {
      this.$refs['dgProjects'].instance.cancelEditData()
    },
    popupCloseButtonClick() {
      this.$refs['dgProjects'].instance.refresh()
      this.popupForCreateProjectVisible = false
    },
    onShowingCreateProjectPopup() {
      this.$refs['CreateProjectTemplate'].onShowing()
    },
    openProject(e) {
      const resolvedRoute = this.$router.resolve({
        name: 'Проект',
        params: { projectId: e.row.key, name: e.row.data.name }
      })
      window.open(resolvedRoute.href, '_self')
    },
    customSaveButtonClick(e) {
      var res = e.validationGroup.validate()
      if (res.isValid) {
        axios.post(`/project/update?id=${this.projectId}`, this.editRowValue).then((res) => {
          if (res == undefined || res.status != 200 || res.data != true)
            notify(
              { message: 'Ошибка при обновлении проекта', type: 'error', displayTime: 2000 },
              { position: 'center' }
            )
          else {
            this.$refs['dgProjects'].instance.refresh()
            this.customCancelButtonClick()
          }
        })
      }
    },
    async editingStart(e) {
      this.projectId = e.key
      this.uploadUrl = `http://127.0.0.1:8000/file/upload?id=${this.projectId}`
      await axios
        .get('/project/get-data-for-editing', {
          params: {
            id: this.projectId
          }
        })
        .then((res) => {
          this.editRowValue = res.data.project
          this.gDsTimeSeries = res.data.time_series
        })
        .catch((error) => {
          console.error(error)
        })
      this.$refs['dgProjects'].instance.refresh()
    },
    acceptFUData(gDsTimeSeries) {
      this.gDsTimeSeries = gDsTimeSeries
    }
  }
}
</script>

<style scoped>
td {
  padding-bottom: 10px;
}

.BigButtonCancel {
  margin-top: 10px;
}

div {
  margin-top: 10px;
}
</style>

<style>
.dx-popup-content-scrollable {
  overflow: hidden;
  overscroll-behavior: none;
}

.dx-button {
  margin: 2px;
}

.buttons {
  margin-right: 5px;
  margin-bottom: 5px;
  position: absolute;
  right: 0;
  bottom: 0;
}

.hint {
  font-family: Verdana, Geneva, sans-serif;
  font-size: 16px;
  letter-spacing: 0px;
  word-spacing: 0px;
  color: #200c0c;
  font-weight: 400;
  text-decoration: none;
  font-style: normal;
  font-variant: normal;
  text-transform: none;
  text-align: start;
}
</style>
