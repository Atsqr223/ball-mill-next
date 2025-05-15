import mqtt from 'mqtt'
import { db } from './db'
import { sensorData, acquisitionSessions } from './schema'
import { eq } from 'drizzle-orm'

class MQTTClient {
  private client: mqtt.Client | null = null
  private static instance: MQTTClient | null = null

  private constructor() {}

  static getInstance(): MQTTClient {
    if (!MQTTClient.instance) {
      MQTTClient.instance = new MQTTClient()
    }
    return MQTTClient.instance
  }

  connect() {
    if (this.client) return

    this.client = mqtt.connect(process.env.MQTT_BROKER_URL!, {
      username: process.env.MQTT_USERNAME,
      password: process.env.MQTT_PASSWORD,
    })

    this.client.on('connect', () => {
      console.log('Connected to MQTT broker')
      this.client?.subscribe('ball-mill/+/sensor/+')
    })

    this.client.on('message', async (topic, message) => {
      try {
        const [, locationId, , sensorId] = topic.split('/')
        const data = JSON.parse(message.toString())

        // Find active acquisition session
        const session = await db.query.acquisitionSessions.findFirst({
          where: eq(acquisitionSessions.status, 'active')
        })

        if (session) {
          // Store sensor data
          await db.insert(sensorData).values({
            sessionId: session.id,
            sensorId: parseInt(sensorId),
            value: data.value,
            timestamp: new Date(),
            analysisResults: data.analysis || null
          })
        }
      } catch (error) {
        console.error('Error processing MQTT message:', error)
      }
    })

    this.client.on('error', (error) => {
      console.error('MQTT client error:', error)
    })
  }

  disconnect() {
    if (this.client) {
      this.client.end()
      this.client = null
    }
  }

  publish(topic: string, message: string) {
    if (this.client) {
      this.client.publish(topic, message)
    }
  }
}

export const mqttClient = MQTTClient.getInstance() 