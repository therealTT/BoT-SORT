import queue
import numpy as np

from scipy.spatial.distance import cdist
import faiss

from tracker.bot_sort import BoTSORT


class MultiCameraTracking:
    def __init__(self, args, frame_rate=30,time_window=50, global_match_thresh=0.35):

        self.time = 0
        self.last_global_id = 0
        self.global_ids_queue = queue.Queue()
        assert time_window >= 1
        self.time_window = time_window  # should be greater than time window in scts
        assert 0 <= global_match_thresh <= 1
        self.global_match_thresh = global_match_thresh
        self.num_sources = len(args.path)
        self.all_tracks = {}
        self.cam_id_list = []
        self.all_features = []
        self.all_track_ids = []
        self.indexes = []
        self.trackers = []
        self.num = 0
        self.tracks_in_use = []
        
        
        d = 2048
        
        for i in range(self.num_sources): 
            index = faiss.IndexFlatL2(d)
            self.indexes.append(index) 
        print(self.indexes)

        for i in range(self.num_sources):
            self.trackers.append(BoTSORT(args, frame_rate=args.fps))
        print(self.trackers)

        
    def process(self, output_results, img, cam_id):

        new_tracks = self.trackers[cam_id].update(output_results, img)

        return_tracks = []
        for track in new_tracks:
            merged = False
            best_distance = 0.8 
            index = self.indexes[cam_id]
            if track.curr_feat is not None:

                #self.all_features.append(track.curr_feat)

                # self.all_track_ids.append(track.track_id)
                # self.cam_id_list.append(cam_id)
                print(track.track_id, "current track original ID")
                print(cam_id,"original cam id")
                #all_features = np.array(self.all_features)
                query_feature = track.curr_feat.reshape(1,-1).astype('float32')
                if self.num >= 1:
                    for cam in range(self.num_sources):
                        print(cam,"iterating cam id")
                        if cam != cam_id:
                            print(cam,"iterating cam id but not the same cam id as original")
                            D, I = self.indexes[cam].search(query_feature, 1)
                            distance = D[0][0]
                            print(distance, "closest distance")
                            if distance < best_distance:
                                best_distance = distance
                                nearest_index = I[0][0]
                                print(nearest_index, "index of the track")
                                nearest_track_id = self.all_tracks[cam][nearest_index]
                                print(nearest_track_id, "corresponding track id")
                                self.tracks_in_use.append(nearest_track_id)
                                merged = True
                    if merged == False:
                        D, I = self.indexes[cam_id].search(query_feature, 1)
                        print(cam_id,"should be the same as original cam id")
                        distance = D[0][0]
                        print(distance, "distance when there isnt one is diff cam")
                        if distance < best_distance:
                            best_distance = distance
                            nearest_index = I[0][0]
                            nearest_track_id = self.all_tracks[cam_id][nearest_index]
                            print(nearest_track_id, "track id in same cam")
                            self.tracks_in_use.append(nearest_track_id)
                        else:
                            nearest_track_id = max(set(self.tracks_in_use)) + 1
                            print(nearest_track_id, "track id when no matches")
                else:
                    nearest_track_id = track.track_id
                    print(nearest_track_id, "track id for first one")
                if cam_id in self.all_tracks:
                    self.all_tracks[cam_id].append(nearest_track_id)
                else:
                    self.all_tracks[cam_id] = [nearest_track_id]

                self.num += 1
                return_tracks.append(Merge(nearest_track_id, track.tlwh, track.score, 'unknown', cam_id))
                index.add(track.curr_feat.reshape(1,-1).astype('float32'))
            # if neighbour == False:
            #     D, I = self.indexes[cam_id].search(query_feature, 1)
            #     same_distance = D[0][0]
            #     if same_distance < best_distance:
            #         best_distance = distance
            #         nearest_index = I[0][0]
            #         nearest_track_id = self.all_tracks[cam][nearest_index]
            #     else:
            #         continue

            #print(self.all_tracks)

            # for i in range(self.num,len(all_features)):
            #     self.num += 1
            #     query_feature = all_features[i].reshape(1, -1)
            #     if cam_id != 0:
            #         best_distance = 1
            #         for j in range(1, cam_id+1):
            #             D, I = self.indexes[j - 1].search(query_feature, 1)
            #             distance = D[0][0]
            #             if distance < best_distance:
            #                 best_distance = distance
            #                 nearest_index = I[0][0]
            #                 print(nearest_index)
            #                 nearest_track_id = self.all_tracks[j - 1][nearest_index] 
            #             else:
            #                 continue

                    
                #     if best_distance < 0.1:
                #         print("merging {} with {}".format(track.track_id, nearest_track_id))
                #         merged = True
                #         #track.track_id = nearest_track_id
                # else:
                #     continue
        return return_tracks

class Merge:
    def __init__(self, track_id, tlwh, score, name, cam_id):
        self.track_id = track_id
        self.tlwh = tlwh
        self.score = score
        self.name = name
        self.cam_id = cam_id
        # Other attributes...










# features = sct.get_features_keep()
# try:
#     if features.shape[0] > 0:
#         all_features = np.concatenate((all_features, features), axis=0)
# except:
#     if len(features) > 0:
#         features = np.array(features)  # Convert features to a NumPy array
#         all_features = np.concatenate((all_features, features), axis=0)

# print(all_features.shape)
# self.detections += sct.get_detections()
# print(len(self.detections))
# for i in all_tracks:
#     print(i.track_id)