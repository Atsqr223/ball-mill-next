import { pgTable, serial, varchar, timestamp, integer, doublePrecision, jsonb, index, uniqueIndex, real, text } from 'drizzle-orm/pg-core'

export const locations = pgTable('locations', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  youtubeStreamId: varchar('youtube_stream_id', { length: 255 }),
  status: varchar('status', { length: 50 }).notNull().default('active'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
})

export const sensors = pgTable('sensors', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 255 }).notNull(),
  type: varchar('type', { length: 50 }).notNull(), // 'LD', 'ACCELEROMETER', 'RADAR'
  locationId: integer('location_id').references(() => locations.id).notNull(),
  status: varchar('status', { length: 50 }).notNull().default('active'),
  configuration: jsonb('configuration'), // Sensor-specific configuration
  description: text('description'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  locationIdx: index('sensors_location_idx').on(table.locationId),
  typeIdx: index('sensors_type_idx').on(table.type),
  nameLocationIdx: uniqueIndex('sensors_name_location_idx').on(table.name, table.locationId),
}))

export const sensorData = pgTable('sensor_data', {
  id: serial('id').primaryKey(),
  sensorId: integer('sensor_id').references(() => sensors.id).notNull(),
  acquisitionSessionId: integer('acquisition_session_id').references(() => acquisitionSessions.id), // Optional reference to an acquisition session
  // LD Sensor data
  distance: real('distance'),
  // Accelerometer data
  accelerationX: real('acceleration_x'),
  accelerationY: real('acceleration_y'),
  accelerationZ: real('acceleration_z'),
  // Radar data
  radar: real('radar'),
  // Time values
  sensorTime: real('sensor_time'), // High-precision decimal time from sensor
  timestamp: timestamp('timestamp').notNull(), // Database record timestamp
  metadata: jsonb('metadata'), // Additional measurement metadata
  createdAt: timestamp('created_at').defaultNow(),
}, (table) => ({
  sensorIdx: index('sensor_data_sensor_idx').on(table.sensorId),
  sessionIdx: index('sensor_data_session_idx').on(table.acquisitionSessionId),
  timestampIdx: index('sensor_data_timestamp_idx').on(table.timestamp),
  sensorTimeIdx: index('sensor_data_sensor_time_idx').on(table.sensorTime),
}))

export const acquisitionSessions = pgTable('acquisition_sessions', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').references(() => locations.id).notNull(),
  sensorId: integer('sensor_id').references(() => sensors.id).notNull(),
  status: varchar('status', { length: 50 }).notNull().default('in_progress'),
  startTime: timestamp('start_time').notNull().defaultNow(),
  endTime: timestamp('end_time'),
  fileName: varchar('file_name', { length: 255 }),
  metadata: jsonb('metadata'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
}, (table) => ({
  locationIdx: index('acquisition_sessions_location_idx').on(table.locationId),
  sensorIdx: index('acquisition_sessions_sensor_idx').on(table.sensorId),
  startTimeIdx: index('acquisition_sessions_start_time_idx').on(table.startTime),
}))

export const ballMillPositions = pgTable('ball_mill_positions', {
  id: serial('id').primaryKey(),
  locationId: integer('location_id').notNull(),
  x: doublePrecision('x').notNull(),
  y: doublePrecision('y').notNull(),
  z: doublePrecision('z').notNull(),
  timestamp: timestamp('timestamp').defaultNow(),
  createdAt: timestamp('created_at').defaultNow(),
}, (table) => ({
  locationIdx: index('ball_mill_positions_location_idx').on(table.locationId),
  timestampIdx: index('ball_mill_positions_timestamp_idx').on(table.timestamp),
}))
