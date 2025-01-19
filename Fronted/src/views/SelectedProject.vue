<template>
  <div class="container-fluid">
    <h2 class="text-center">{{ this.$route.params.name }}</h2>
    <div class="row">
      <div class="col">
        <DxDataGrid
          ref="dgTimeSeries"
          :column-hiding-enabled="false"
          :data-source="this.gDsTimeSeries"
          :remote-operations="false"
          :row-Alternation-Enabled="true"
          :show-borders="true"
          :show-row-lines="true"
          :word-wrap-enabled="true"
          @key-down="KeyDown"
          @saved="saveChangeTimeSeries"
          :height="250"
        >
          <DxColumn caption="Координаты" data-field="name" :allowEditing="false" />
          <DxColumn caption="Описание" data-field="description" :allowEditing="false" />
          <DxColumn
            caption="Цвет"
            data-field="color"
            :width="140"
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
            />
          </template>
          <DxColumn caption="Отображение" data-field="visible" :width="120" />

          <DxGroupPanel :visible="false" />
          <DxGrouping :auto-expand-all="false" />
          <DxFilterRow :visible="false" />
          <DxHeaderFilter :visible="false" />
          <DxScrolling mode="standard" />

          <DxEditing :allow-updating="true" mode="cell" />
        </DxDataGrid>
        <div style="margin-top: 5px">
          <DxButton
            :disabled="!this.gDsTimeSeries.length"
            hint="Найти примитив"
            @click="primitiveSearchButtonClick"
            >Найти примитив</DxButton
          >
        </div>
      </div>
      <div class="col">
        <DxDataGrid
          ref="dgPrimitives"
          :column-hiding-enabled="false"
          :data-source="this.gDsPrimitives"
          :remote-operations="false"
          :row-Alternation-Enabled="true"
          :show-borders="true"
          :show-row-lines="true"
          :word-wrap-enabled="true"
          @key-down="KeyDown"
          @saved="savedChangePrimitive"
          :height="300"
        >
          <DxColumn caption="Примитив" data-field="name" :allowEditing="false" />
          <DxColumn
            caption="Длина подпоследовательности"
            data-field="subseqLen"
            alignment="left"
            :width="180"
            :allowEditing="false"
          />
          <DxColumn
            caption="Цвет"
            data-field="color"
            :width="140"
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
            />
          </template>
          <DxColumn caption="Отображение" data-field="visible" :width="120" />

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

  <div style="margin: 30px">
    <DxChart :data-source="this.chartData" ref="dxChart">
      <DxCommonSeriesSettings :argument-field="this.axisLabel" />
      <DxSeries
        v-for="item in this.series"
        :key="item.name"
        :name="item.name"
        :value-field="item.field"
        :color="item.color"
        :visible="item.visible"
        :type="'line'"
      >
        <DxPoint :visible="false" />
      </DxSeries>

      <DxArgumentAxis :visual-range="this.range">
        <DxMinorTick :visible="false" />
        <DxTick :visible="true" />
        <DxLabel overlapping-behavior="stagger" />
      </DxArgumentAxis>
      <DxTooltip :enabled="true" />
      <DxCrosshair :enabled="true">
        <DxHorizontalLine :visible="false" />
        <DxLabel :visible="true" />
      </DxCrosshair>
      <DxLegend :visible="true" />
      <DxExport :enabled="true" />

      <DxZoomAndPan
        :drag-to-zoom="true"
        :allow-mouse-wheel="true"
        value-axis="both"
        argument-axis="both"
        pan-key="shift"
      />
    </DxChart>

    <DxRangeSelector :data-source="this.chartData" v-model:value="this.range">
      <DxRsChart>
        <DxRsSeries
          v-for="item in this.series"
          :key="item.name"
          :name="item.name"
          :value-field="item.field"
          :color="item.color"
          :visible="item.visible"
          :argument-field="this.axisLabel"
        >
        </DxRsSeries>
      </DxRsChart>
      <DxSize :height="100" />
      <DxScale><DxRsLabel :visible="false" /></DxScale>
      <DxBehavior value-change-mode="onHandleMove" />
      <DxSliderMarker color="#13279c" />
      <DxSliderHandle color="#13279c" :opacity="10" :width="5" />
    </DxRangeSelector>
  </div>
  <SearchPrimitivePopup :tsIds="this.tsIds" @childData="acceptData" ref="SearchPrimitivePopup" />
</template>

<script>
import {
  DxDataGrid,
  DxColumn,
  DxFilterRow,
  DxHeaderFilter,
  DxGroupPanel,
  DxGrouping,
  DxScrolling,
  DxEditing
} from 'devextreme-vue/data-grid'
import axios from 'axios'
import DxColorBox from 'devextreme-vue/color-box'
import DxChart, {
  DxArgumentAxis,
  DxSeries,
  DxPoint,
  DxCommonSeriesSettings,
  DxExport,
  DxLegend,
  DxLabel,
  DxCrosshair,
  DxHorizontalLine,
  DxTooltip,
  DxZoomAndPan,
  DxMinorTick,
  DxTick
} from 'devextreme-vue/chart'
import {
  DxRangeSelector,
  DxSize,
  DxScale,
  DxChart as DxRsChart,
  DxBehavior,
  DxSeries as DxRsSeries,
  DxLabel as DxRsLabel,
  DxSliderMarker,
  DxSliderHandle
} from 'devextreme-vue/range-selector'
import DxButton from 'devextreme-vue/button'
import ruMessages from 'devextreme/localization/messages/ru.json'
import { locale, loadMessages } from 'devextreme/localization'
import notify from 'devextreme/ui/notify'
import SearchPrimitivePopup from '@/components/SearchPrimitivePopup.vue'

export default {
  name: 'SelectedProjectView',
  components: {
    DxDataGrid,
    DxColumn,
    DxFilterRow,
    DxHeaderFilter,
    DxGroupPanel,
    DxGrouping,
    DxScrolling,
    DxEditing,
    DxColorBox,
    DxChart,
    DxArgumentAxis,
    DxSeries,
    DxPoint,
    DxCommonSeriesSettings,
    DxExport,
    DxLegend,
    DxLabel,
    DxCrosshair,
    DxHorizontalLine,
    DxTooltip,
    DxZoomAndPan,
    DxRangeSelector,
    DxSize,
    DxScale,
    DxRsChart,
    DxBehavior,
    DxRsSeries,
    DxRsLabel,
    DxSliderMarker,
    DxSliderHandle,
    DxButton,
    DxMinorTick,
    DxTick,
    SearchPrimitivePopup
  },
  data() {
    return {
      gDsTimeSeries: [],
      gDsPrimitives: [],
      chartData: [],
      series: [],
      range: [],
      axisLabel: 'stamp',
      tsIds: []
    }
  },
  async mounted() {
    let isRight = true
    this.gDsTimeSeries = await axios
      .get('/time-series/get-to-display', {
        params: {
          project_id: this.$route.params.projectId
        }
      })
      .then((res) => {
        return res.data
      })
      .catch((error) => {
        notify({ message: error.response.data.detail, type: 'error' }, { position: 'center' })
        this.$router.push('/')
        isRight = false
      })
    if (isRight) {
      if (this.gDsTimeSeries.length) {
        this.tsIds = this.gDsTimeSeries.map((i) => i.id)
        this.gDsTimeSeries.forEach((v, i) => {
          v.color =
            i > 9
              ? '#' + (0x1000000 + Math.random() * 0xffffff).toString(16).substring(1, 7)
              : this.$store.state.tsColors[i].color
          v.visible = false
        })
      }
      this.gDsPrimitives = await axios
        .get('/primitive/get-to-display', {
          params: {
            project_id: this.$route.params.projectId
          }
        })
        .then((res) => {
          return res.data
        })
        .catch((error) => {
          console.error(error)
        })
      this.transformationPrimitivesData()

      this.createDataToDisplay()
    }
  },
  created() {
    loadMessages(ruMessages)
    locale('ru-RU')
  },
  methods: {
    transformationPrimitivesData() {
      if (this.gDsPrimitives.length) {
        this.gDsPrimitives.forEach((v, i) => {
          v.color =
            i > 9
              ? '#' + (0x1000000 + Math.random() * 0xffffff).toString(16).substring(1, 7)
              : this.$store.state.prColors[i].color
          v.visible = false
        })
      }
    },
    createDataToDisplay() {
      this.chartData = []
      this.series = []
      this.gDsTimeSeries.forEach((v, i) => {
        this.series.push({ field: `${v.id}`, name: v.name, color: v.color, visible: v.visible })
        if (i == 0) {
          if (v.stamp.length != 0) {
            v.stamp.forEach((k, j) => {
              this.chartData.push({ num: j, stamp: new Date(k).toLocaleString() })
              this.chartData[j][v.id] = k
            })
          } else {
            for (let i = 0; i < v.value.length; i++) {
              this.chartData.push({ num: i, stamp: i })
            }
          }
        }
        v.value.forEach((k, j) => {
          this.chartData[j][v.id] = k
        })
      })
      this.addPrimitivesInDataToDisplay()
    },
    addPrimitivesInDataToDisplay() {
      this.gDsPrimitives.forEach((v) => {
        this.series.push({
          field: `${v.key}`,
          name: `${v.name}(${v.subseqLen})`,
          color: v.color,
          visible: v.visible
        })
        this.chartData.forEach((k) => {
          k[v.key] = null
        })
        if ('Матричный профиль' == v.name.split('(')[0]) {
          v.nnDist.forEach((c, j) => {
            this.chartData[j][v.key] = c
          })
        } else {
          v.indexes.forEach((c) => {
            this.chartData[c][v.key] = this.chartData[c][v.ts_id]
          })
        }
      })
    },
    saveChangeTimeSeries(e) {
      this.series.forEach((v) => {
        if (v.field == e.changes[0].data.id) {
          v.color = e.changes[0].data.color
          v.visible = e.changes[0].data.visible
        }
      })
    },
    async savedChangePrimitive(e) {
      let isMP = await this.saveChangePrimitive(e)
      if (isMP) this.$refs['dxChart'].instance.refresh()
    },
    saveChangePrimitive(e) {
      let isMP = false
      this.series.forEach((v) => {
        if (v.field == e.changes[0].data.key) {
          if ('Матричный профиль' == v.name.split('(')[0]) {
            this.axisLabel = e.changes[0].data.visible ? 'num' : 'stamp'
            isMP = true && e.changes[0].data.visible
          }
          v.color = e.changes[0].data.color
          v.visible = e.changes[0].data.visible
        }
      })
      return isMP
    },
    KeyDown(e) {
      if (e.event.key == 'Enter') {
        e.event.preventDefault()
      }
    },
    primitiveSearchButtonClick() {
      this.$refs['SearchPrimitivePopup'].start(true)
    },
    async acceptData(editData, selectedItemKeys) {
      let primitives = []
      selectedItemKeys.forEach((el) => {
        primitives.push({
          ts_id: el.id,
          primitive_name: editData.primitive,
          subseqLen: editData.subseqLen,
          topK: editData.topK
        })
      })
      this.gDsPrimitives = await axios.post('/primitive/find', primitives).then((res) => {
        return res.data
      })
      this.transformationPrimitivesData()
      this.createDataToDisplay()
    }
  }
}
</script>

<style scoped></style>
