from __future__ import annotations

from app.tools.contracts import ToolRequest, ToolResponse, ToolResultItem


_UNIT_FACTORS_TO_NM = {
    "m": 1e9,
    "mm": 1e6,
    "um": 1e3,
    "nm": 1.0,
    "pm": 1e-3,
}


class MeasurementNormalizerTool:
    name = "measurement_normalizer"

    def execute(self, request: ToolRequest) -> ToolResponse:
        value = request.payload.get("value")
        unit = str(request.payload.get("unit", "")).strip().lower()

        if value is None:
            return ToolResponse(
                tool_name=self.name,
                status="error",
                errors=["missing value"],
            )

        if unit not in _UNIT_FACTORS_TO_NM:
            return ToolResponse(
                tool_name=self.name,
                status="error",
                errors=[f"unsupported unit '{unit}'"],
            )

        normalized_value = float(value) * _UNIT_FACTORS_TO_NM[unit]

        result = ToolResultItem(
            id="normalized_measurement",
            source_id="computed",
            chunk_id=None,
            title="normalized_measurement",
            text=None,
            score=1.0,
            metadata={
                "input_value": value,
                "input_unit": unit,
                "normalized_value": round(normalized_value, 6),
                "normalized_unit": "nM",
            },
        )

        return ToolResponse(
            tool_name=self.name,
            status="ok",
            results=[result],
        )