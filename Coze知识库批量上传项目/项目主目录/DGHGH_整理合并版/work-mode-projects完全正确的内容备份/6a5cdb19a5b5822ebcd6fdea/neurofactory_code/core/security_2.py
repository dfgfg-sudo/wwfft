openapi: 3.0.0
info:
  title: 智能天气服务插件
  version: 2.0.0
  description: |
    提供实时天气、3日预报、空气质量、生活建议、健康指数、出行指南等完整功能。
    数据源：和风天气（模拟），实际可替换为任意提供 OpenAPI 的服务。
  contact:
    name: 技术团队
    email: dev@example.com

servers:
  - url: https://api.weather-service.com/v1
    description: 生产环境

securitySchemes:
  ApiKeyAuth:
    type: apiKey
    in: header
    name: X-API-Key

security:
  - ApiKeyAuth: []

paths:
  /weather/current:
    post:
      operationId: getCurrentWeather
      summary: 获取实时天气
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [city]
              properties:
                city:
                  type: string
                  example: 北京
                district:
                  type: string
                  example: 海淀区
                language:
                  type: string
                  enum: [zh-CN, en-US]
                  default: zh-CN
                units:
                  type: string
                  enum: [metric, imperial]
                  default: metric
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  message:
                    type: string
                  data:
                    type: object
                    properties:
                      location:
                        type: object
                        properties:
                          city: { type: string }
                          district: { type: string }
                      current:
                        type: object
                        properties:
                          temperature: { type: integer }
                          humidity: { type: integer }
                          weather: { type: string }
                          wind_speed: { type: number }
                      recommendations:
                        type: object
                        properties:
                          clothing: { type: string }
                          activity: { type: string }

  /weather/forecast:
    post:
      operationId: getForecast
      summary: 获取未来3天预报
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [city]
              properties:
                city: { type: string }
                days:
                  type: integer
                  minimum: 1
                  maximum: 7
                  default: 3
      responses:
        '200':
          description: 预报数据

components:
  schemas:
    ErrorResponse:
      type: object
      properties:
        code: { type: integer }
        message: { type: string }
        details: { type: string }